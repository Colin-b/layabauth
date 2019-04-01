import datetime
import json
import logging
import os
import re
from typing import Tuple
from urllib.parse import urlparse

import celery.result
import flask
from celery import Celery
from celery.task import control
from flask_restplus import Resource, fields, Namespace
from redis import Redis

_STATUS_ENDPOINT = "status"
_RESULT_ENDPOINT = "result"

logger = logging.getLogger("celery_server")


class AsyncNamespaceProxy:
    """
    Flask rest-plus Namespace proxy.
    This proxy namespace add a decorator 'async_route' that will generate 2 extra endpoint : /status and /result
    to query the status or the result of the celery task
    """

    def __init__(self, namespace: Namespace, celery_app: Celery):
        self.__namespace = namespace
        self.__celery_app = celery_app
        task_status_model = namespace.model(
            "AsyncTaskStatusModel",
            {
                "task_id": fields.String(required=True, description="Task Id."),
                "url": fields.String(
                    required=True, description="URL when task status can be checked."
                ),
            },
        )
        self.how_to_get_async_status_doc = {
            "responses": {
                202: (
                    "Computation started.",
                    task_status_model,
                    {"headers": {"location": "URL to fetch computation status from."}},
                )
            }
        }

    def __getattr__(self, name):
        return getattr(self.__namespace, name)

    def async_route(self, endpoint: str, serializer=None, to_response=None):
        """
        Add an async route endpoint.
        :param endpoint: value of the exposes endpoint ex: /foo
        :param serializer: In case the response needs serialization, a single model or a list of model.
        If a list is given, the output will be treated (serialized) and documented as a list
        :param to_response: In case the task result needs to be processed before returning it to client.
        This is a function taking the task result as parameter (and path parameters if needed) and returning a result.
        Default to returning unmodified task result.
        :return: route decorator
        """

        def wrapper(cls):
            # Create the requested route
            self.__namespace.route(endpoint)(cls)
            # Create two additional endpoints to retrieve status and result
            _build_result_endpoints(
                cls.__name__,
                endpoint,
                self.__namespace,
                self.__celery_app,
                serializer,
                to_response,
            )
            return cls

        return wrapper


def build_celery_application(config: dict, *apps: str, **kwargs) -> Celery:
    """
    This function should be called within a python module called 'celery_server.py'
    Build a celery application with given configuration and modules
    :param config: Dictionary with following structure: {
        'celery': {
            'broker': ...,
            'backend': ...,
        }
    }
    :param apps: celery application modules
    :param kwargs: Additional Celery arguments
    To add celery configuration parameter, you should provide a dictionary named changes with those parameters.
    As in changes={'task_serializer': 'pickle'}
    :return: Celery Application
    """
    namespace = _namespace()
    queue = _queue()

    logger.info(f"Starting Celery server on {namespace} namespace")

    return Celery(
        "celery_server",
        broker=config["celery"]["broker"],
        # Store the state and return values of tasks
        backend=config["celery"]["backend"],
        namespace=namespace,
        include=apps,
        changes={
            "worker_hijack_root_logger": False,
            # Use pickle instead of msgpack for now as there is a bug in Celery 4.3.0 with redis
            "task_serializer": "pickle",
            "result_serializer": "pickle",
            "accept_content": ["pickle"],
            "task_compression": "gzip",
            "task_default_queue": queue,
            "task_default_exchange": queue,
            "task_default_routing_key": queue,
            **kwargs.pop("changes", {}),
        },
        **kwargs,
    )


def _base_url() -> str:
    """
    Return client original requested URL in order to make sure it works behind a reverse proxy as well.
    Without parameters.
    """
    if "X-Original-Request-Uri" in flask.request.headers:
        parsed = urlparse(flask.request.headers["X-Original-Request-Uri"])
        return f'{flask.request.scheme}://{flask.request.headers["Host"]}{parsed.path}'
    return flask.request.base_url


def how_to_get_async_status(celery_task) -> flask.Response:
    url = f"{_base_url()}/{_STATUS_ENDPOINT}/{celery_task.id}"
    status = flask.Response()
    status.status_code = 202
    status.content_type = "application/json"
    status.headers["location"] = url
    status.data = json.dumps({"task_id": celery_task.id, "url": url})
    return status


def _get_celery_status(celery_task_id: str, celery_app: Celery) -> flask.Response:
    celery_task = celery.result.AsyncResult(celery_task_id, app=celery_app)

    if celery_task.ready():
        status = flask.Response()
        status.status_code = 303
        status.headers["location"] = _base_url().replace(
            f"/{_STATUS_ENDPOINT}/", f"/{_RESULT_ENDPOINT}/"
        )
        return status

    # TODO Add more information such as request initial time, and maybe intermediate client status
    return flask.jsonify({"state": celery_task.state})


def _get_celery_result(celery_app: Celery, celery_task_id: str):
    celery_task = celery.result.AsyncResult(celery_task_id, app=celery_app)
    return celery_task.get(propagate=True)


def _conditional_marshalling(namespace: Namespace, response_model):
    def wrapper(func):
        if response_model is not None:
            return namespace.marshal_with(
                response_model[0]
                if isinstance(response_model, list)
                else response_model,
                as_list=isinstance(response_model, list),
            )(func)
        return func

    return wrapper


def _build_result_endpoints(
    base_clazz,
    endpoint_root: str,
    namespace: Namespace,
    celery_application: Celery,
    response_model,
    to_response: callable,
):
    @namespace.route(f"{endpoint_root}/{_RESULT_ENDPOINT}/<string:task_id>")
    class AsyncTaskResult(Resource):
        @_conditional_marshalling(namespace, response_model)
        @namespace.doc(f"get_{_snake_case(base_clazz)}_result")
        def get(self, task_id: str, **kwargs):
            """
            Retrieve result for provided task.
            """
            result = _get_celery_result(celery_application, task_id)
            return to_response(result, **kwargs) if to_response else result

    @namespace.route(f"{endpoint_root}/{_STATUS_ENDPOINT}/<string:task_id>")
    @namespace.doc(
        responses={
            200: (
                "Task is still computing.",
                namespace.model(
                    "CurrentAsyncState",
                    {
                        "state": fields.String(
                            description="Indicates current computation state.",
                            required=True,
                            example="PENDING",
                        )
                    },
                ),
            ),
            303: (
                "Result is available.",
                None,
                {"headers": {"location": "URL to fetch results from."}},
            ),
            500: (
                "An unexpected error occurred.",
                fields.String(description="Stack trace.", required=True),
            ),
        }
    )
    class AsyncTaskStatus(Resource):
        @namespace.doc(f"get_{_snake_case(base_clazz)}_status")
        def get(self, task_id: str, **kwargs):
            """
            Retrieve status for provided task.
            """
            return _get_celery_status(task_id, celery_application)


def _snake_case(name: str) -> str:
    if "_" in name:
        raise ValueError(f"{name} should be Camel Case and should not contain any _")
    s1 = re.sub("(.)([A-Z][a-z]+)", r"\1_\2", name)
    return re.sub("([a-z0-9])([A-Z])", r"\1_\2", s1).lower()


def _namespace() -> str:
    """
    Workers are started using CONTAINER_NAME environment variable as namespace or local.
    Followed by a unique identifier per machine (HOSTNAME environment variable or localhost)
    """
    return (
        f"{os.getenv('CONTAINER_NAME', 'local')}_{os.getenv('HOSTNAME', 'localhost')}"
    )


def _queue():
    """
    Workers are started using CONTAINER_NAME environment variable as queue or local.
    """
    return os.getenv("CONTAINER_NAME", "local")


def redis_health_details(config: dict) -> Tuple[str, dict]:
    try:
        redis = Redis.from_url(config["celery"]["backend"])
        redis.ping()

        namespace = _namespace()
        keys = redis.keys(namespace)

        if not keys or not isinstance(keys, list):
            return (
                "fail",
                {
                    "redis:ping": {
                        "componentType": "component",
                        "status": "fail",
                        "time": datetime.datetime.utcnow().isoformat(),
                        "output": f"Namespace {namespace} cannot be found in {keys}",
                    }
                },
            )

        return (
            "pass",
            {
                "redis:ping": {
                    "componentType": "component",
                    "observedValue": f"Namespace {namespace} can be found.",
                    "status": "pass",
                    "time": datetime.datetime.utcnow().isoformat(),
                }
            },
        )
    except Exception as e:
        return (
            "fail",
            {
                "redis:ping": {
                    "componentType": "component",
                    "status": "fail",
                    "time": datetime.datetime.utcnow().isoformat(),
                    "output": str(e),
                }
            },
        )


def health_details():
    try:
        worker_name = f"celery@{_namespace()}"
        workers = control.ping(destination=[worker_name])
        if not workers:
            return (
                "fail",
                {
                    "celery:ping": {
                        "componentType": "component",
                        "status": "fail",
                        "time": datetime.datetime.utcnow().isoformat(),
                        "output": f"No {worker_name} workers could be found.",
                    }
                },
            )

        return (
            "pass",
            {
                "celery:ping": {
                    "componentType": "component",
                    "observedValue": workers,
                    "status": "pass",
                    "time": datetime.datetime.utcnow().isoformat(),
                }
            },
        )
    except Exception as e:
        return (
            "fail",
            {
                "celery:ping": {
                    "componentType": "component",
                    "status": "fail",
                    "time": datetime.datetime.utcnow().isoformat(),
                    "output": str(e),
                }
            },
        )
