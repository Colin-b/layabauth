# -*- coding: utf-8 -*-

import logging
import os
import re
from urllib.parse import urlparse

import flask
from celery import Celery
from celery import result as celery_results
from flask_restplus import Resource

_STATUS_ENDPOINT = 'status'
_RESULT_ENDPOINT = 'result'

logger = logging.getLogger('celery_server')


class AsyncNamespaceProxy:
    """
    Flask rest-plus Namespace proxy.
    This proxy namespace add a decorator 'async_route' that will generate 2 extra endpoint : /status and /result
    to query the status or the result of the celery task
    """

    def __init__(self, namespace, celery_app, exception_responses):
        self.__namespace = namespace
        self.__celery_app = celery_app
        self.__exception_responses = exception_responses

    def __getattr__(self, name):
        return getattr(self.__namespace, name)

    def async_route(self, endpoint, serializer):
        def wrapper(cls):
            ## 1st create the one requested
            self.__namespace.route(endpoint)(cls)
            ## create the 2 extra endpoints '/result' and '/status'
            _build_result_endpoints(cls.__name__, endpoint, self.__namespace, self.__celery_app, serializer,
                                    self.__exception_responses)
            return cls

        return wrapper


def build_celery_application(config: dict, *apps, **kwargs) -> Celery:
    """
    This function should be called within a python module called 'celery_server.py'
    Build a celery application with given configuration and modules
    :param config: Dictionary with following structure: config['celery']['namespace'] config['celery']['broker'] config['celery']['backend']
    :param apps: celery application modules
    :param kwargs: extra kwags passed to Celery class
    :return: Celery Application
    """
    namespace = os.getenv('CONTAINER_NAME', config['celery']['namespace'])

    logger.info(f'Starting Celery server on {namespace} namespace')

    celery_application = Celery(
        'celery_server',
        broker=config['celery']['broker'],
        # Store the state and return values of tasks
        backend=config['celery']['backend'],
        namespace=namespace,
        include=apps,
        **kwargs
    )

    return celery_application


def _base_url():
    """
    Return client original requested URL in order to make sure it works behind a reverse proxy as well.
    Without parameters.
    """
    if 'X-Original-Request-Uri' in flask.request.headers:
        parsed = urlparse(flask.request.headers['X-Original-Request-Uri'])
        return f'{flask.request.scheme}://{flask.request.headers["Host"]}{parsed.path}'
    return flask.request.base_url


def how_to_get_celery_status(celery_task):
    url = f'{_base_url()}{_STATUS_ENDPOINT}/{celery_task.id}'
    status = flask.Response()
    status.status_code = 202
    status.headers['location'] = url
    status.data = f'Computation status can be found using this URL: {url}'
    return status


def _get_celery_status(celery_task_id: str, celery_app: Celery):
    celery_task = celery_results.AsyncResult(celery_task_id, app=celery_app)

    if celery_task.failed():
        raise Exception(f'Computation failed: {celery_task.traceback}')

    if celery_task.ready():
        status = flask.Response()
        status.status_code = 303
        status.headers['location'] = _base_url().replace(f'/{_STATUS_ENDPOINT}/', f'/{_RESULT_ENDPOINT}/')
        return status

    return flask.jsonify({'state': celery_task.state})


def _get_celery_result(celery_app, celery_task_id: str):
    celery_task = celery_results.AsyncResult(celery_task_id, app=celery_app)
    return celery_task.get()


def _build_result_endpoints(base_clazz, endpoint_root, namespace, celery_application, response_model,
                            exception_responses):
    @namespace.route(f'{endpoint_root}/{_RESULT_ENDPOINT}/<string:celery_task_id>')
    @namespace.doc(**exception_responses)
    class CeleryTaskResult(Resource):
        @namespace.marshal_with(response_model[0] if isinstance(response_model, list) else response_model,
                                as_list=isinstance(response_model, list))
        @namespace.doc(f'get_{_snake_case(base_clazz)}_result')
        def get(self, celery_task_id: str):
            """
            Query the result of Celery Async Task
            """
            return _get_celery_result(celery_application, celery_task_id)

    @namespace.route(f'{endpoint_root}/{_STATUS_ENDPOINT}/<string:celery_task_id>')
    @namespace.doc(**exception_responses)
    class CeleryTaskStatus(Resource):
        @namespace.doc(f'get_{_snake_case(base_clazz)}_status')
        def get(self, celery_task_id: str):
            """
            Get the status of Celery Async Task
            """
            return _get_celery_status(celery_task_id, celery_application)


def _snake_case(name: str) -> str:
    if '_' in name:
        raise ValueError(f'{name} should be Camel Case and should not contain any _')
    s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
    return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()
