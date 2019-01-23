import datetime
import json
import logging
import os
import re
from urllib.parse import urlparse

import flask
from celery import Celery
from celery import result as celery_results
from celery.task import control
from flask_restplus import Resource, fields, Namespace

_STATUS_ENDPOINT = 'status'
_RESULT_ENDPOINT = 'result'

logger = logging.getLogger('celery_server')


class AsyncNamespaceProxy:
    """
    Flask rest-plus Namespace proxy.
    This proxy namespace add a decorator 'async_route' that will generate 2 extra endpoint : /status and /result
    to query the status or the result of the celery task
    """

    def __init__(self, namespace: Namespace, celery_app: Celery):
        self.__namespace = namespace
        self.__celery_app = celery_app

    def __getattr__(self, name):
        return getattr(self.__namespace, name)

    def async_route(self, endpoint: str, serializer=None, to_response=None):
        """
        Add an async route endpoint.
        :param endpoint: value of the exposes endpoint ex: /foo
        :param serializer: In case the response needs serialization, a single model or a list of model.
        If a list is given, the output will be treated (serialized) and documented as a list
        :param to_response: In case the task result needs to be processed before returning it to client.
        This is a function taking the task result as parameter and returning a result.
        Default to returning unmodified task result.
        :return: route decorator
        """

        def wrapper(cls):
            # Create the requested route
            self.__namespace.route(endpoint)(cls)
            # Create two additional endpoints to retrieve status and result
            _build_result_endpoints(cls.__name__, endpoint, self.__namespace, self.__celery_app, serializer, to_response)
            return cls

        return wrapper


def build_celery_application(config: dict, *apps, **kwargs) -> Celery:
    """
    This function should be called within a python module called 'celery_server.py'
    Build a celery application with given configuration and modules
    :param config: Dictionary with following structure: {
        'celery': {
            'namespace': ..., (will default to CONTAINER_NAME environment variable)
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
    namespace = os.getenv('CONTAINER_NAME', config['celery']['namespace'])

    logger.info(f'Starting Celery server on {namespace} namespace')

    return Celery(
        'celery_server',
        broker=config['celery']['broker'],
        # Store the state and return values of tasks
        backend=config['celery']['backend'],
        namespace=namespace,
        include=apps,
        **kwargs
    )


def _base_url() -> str:
    """
    Return client original requested URL in order to make sure it works behind a reverse proxy as well.
    Without parameters.
    """
    if 'X-Original-Request-Uri' in flask.request.headers:
        parsed = urlparse(flask.request.headers['X-Original-Request-Uri'])
        return f'{flask.request.scheme}://{flask.request.headers["Host"]}{parsed.path}'
    return flask.request.base_url


def how_to_get_async_status(celery_task) -> flask.Response:
    url = f'{_base_url()}/{_STATUS_ENDPOINT}/{celery_task.id}'
    status = flask.Response(mimetype='application/json')
    status.status_code = 202
    status.content_type = 'application/json'
    status.headers['location'] = url
    status.data = json.dumps({'taskId': celery_task.id, 'url': url})
    return status


how_to_get_async_status_doc = {'responses': {
    202: ('Computation started.', fields.String(), {'headers': {'location': 'URL to fetch computation status from.'}}),
}}


def _get_celery_status(celery_task_id: str, celery_app: Celery) -> flask.Response:
    celery_task = celery_results.AsyncResult(celery_task_id, app=celery_app)

    if celery_task.failed():
        # TODO try to construct the original error
        return flask.make_response(f'{celery_task.traceback}', 500)

    if celery_task.ready():
        status = flask.Response()
        status.status_code = 303
        status.headers['location'] = _base_url().replace(f'/{_STATUS_ENDPOINT}/', f'/{_RESULT_ENDPOINT}/')
        return status

    # TODO Add more information such as request initial time, and maybe intermediate client status
    return flask.jsonify({'state': celery_task.state})


def _get_celery_result(celery_app: Celery, celery_task_id: str):
    celery_task = celery_results.AsyncResult(celery_task_id, app=celery_app)
    return celery_task.get()


def _conditional_marshalling(namespace: Namespace, response_model):
    def wrapper(func):
        if response_model is not None:
            return namespace.marshal_with(response_model[0] if isinstance(response_model, list) else response_model,
                                          as_list=isinstance(response_model, list))(func)
        return func

    return wrapper


def _build_result_endpoints(
        base_clazz,
        endpoint_root: str,
        namespace: Namespace,
        celery_application: Celery,
        response_model,
        to_response: callable):

    @namespace.route(f'{endpoint_root}/{_RESULT_ENDPOINT}/<string:task_id>')
    class AsyncTaskResult(Resource):
        @_conditional_marshalling(namespace, response_model)
        @namespace.doc(f'get_{_snake_case(base_clazz)}_result')
        def get(self, task_id: str):
            """
            Retrieve result for provided task.
            """
            result = _get_celery_result(celery_application, task_id)
            return to_response(result) if to_response else result

    @namespace.route(f'{endpoint_root}/{_STATUS_ENDPOINT}/<string:task_id>')
    @namespace.doc(responses={
        200: ('Task is still computing.', namespace.model('CurrentAsyncState', {
            'state': fields.String(description='Indicates current computation state.', required=True,
                                   example='PENDING'),
        })),
        303: ('Result is available.', None, {'headers': {'location': 'URL to fetch results from.'}}),
        500: ('An unexpected error occurred.', fields.String(description='Stack trace.', required=True))
    })
    class AsyncTaskStatus(Resource):
        @namespace.doc(f'get_{_snake_case(base_clazz)}_status')
        def get(self, task_id: str):
            """
            Retrieve status for provided task.
            """
            return _get_celery_status(task_id, celery_application)


def _snake_case(name: str) -> str:
    if '_' in name:
        raise ValueError(f'{name} should be Camel Case and should not contain any _')
    s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
    return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()


def health_details(config: dict):
    workers = control.ping()
    if not workers:
        return 'fail', {
            'celery:ping': {
                'componentType': 'component',
                'status': 'fail',
                'time': datetime.datetime.utcnow().isoformat(),
                'output': workers
            }
        }

    service_name = os.environ.get('ENV_CONTAINER_NAME')
    if not service_name:
        service_name = f"celery@{config['celery']['namespace']}"
    related_workers = [worker for worker in workers if service_name in worker]
    if not related_workers:
        return 'fail', {
            'celery:ping': {
                'componentType': 'component',
                'status': 'fail',
                'time': datetime.datetime.utcnow().isoformat(),
                'output': workers
            }
        }

    return 'pass', {
        'celery:ping': {
            'componentType': 'component',
            'observedValue': related_workers,
            'status': 'pass',
            'time': datetime.datetime.utcnow().isoformat(),
        }
    }
