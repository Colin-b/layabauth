# -*- coding: utf-8 -*-

import logging
import os
import re
from urllib.parse import urlparse

import flask
from celery import Celery
from celery import result as celery_results
from flask_restplus import Resource

_STATUS_ENDPOINT = '/status'
_RESULT_ENDPOINT = '/result'

logger = logging.getLogger('celery_server')


class AsyncNamespaceProxy:
    """
    Flask rest-plus Namespace proxy.
    This proxy namespace add a decorator 'async_route' that will generate 2 extra endpoint : /status and /result
    to query the status or the result of the celery task
    """

    def __init__(self, namespace, celery_app, exception_response):
        self.__namespace = namespace
        self.__celery_app = celery_app
        self.__exception_response = exception_response

    def __getattr__(self, name):
        return getattr(self.__namespace, name)

    def async_route(self, endpoint, serializer):
        def wrapper(cls):
            _build_result_endpoints(cls.__name__, endpoint, self.__namespace, self.__celery_app, serializer,
                                    self.__exception_response)
            self.__namespace.route(endpoint)(cls)
            return cls
        return wrapper


def add_celery_support(config, apps: list, **kwargs) -> Celery:
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
    status = flask.Response()
    status.status_code = 202
    status.headers['location'] = f'{_base_url()}{_STATUS_ENDPOINT}/{celery_task.id}'
    status.data = f'Computation status can be found using this URL: {_base_url()}{_STATUS_ENDPOINT}/{celery_task.id}'
    return status


def _get_celery_status(celery_task_id: str, celery_app: Celery):
    celery_task = celery_results.AsyncResult(celery_task_id, app=celery_app)

    if celery_task.failed():
        raise Exception(f'Computation failed: {celery_task.traceback}')

    if celery_task.ready():
        status = flask.Response()
        status.status_code = 303
        status.headers['location'] = _base_url().replace(f'{_STATUS_ENDPOINT}/', f'{_RESULT_ENDPOINT}/')
        return status

    return flask.jsonify({'state': celery_task.state})


def _get_celery_result(celery_app, celery_task_id: str):
    celery_task = celery_results.AsyncResult(celery_task_id, app=celery_app)
    return celery_task.get()


def _build_result_endpoints(base_clazz, endpoint_root, namespace, celery_application, response_model,
                            exception_response):
    @namespace.route(f'{endpoint_root}{_RESULT_ENDPOINT}/<string:celery_task_id>')
    @namespace.doc(**exception_response)
    class CeleryTaskResult(Resource):

        @namespace.marshal_with(response_model, as_list=True)
        @namespace.doc(f'get_{_snake_case(base_clazz)}_result')
        def get(self, celery_task_id: str):
            """
            Query the result of Celery Async Task
            """
            return _get_celery_result(celery_application, celery_task_id)

    @namespace.route(f'{endpoint_root}{_STATUS_ENDPOINT}/<string:celery_task_id>')
    @namespace.doc(**exception_response)
    class CeleryTaskStatus(Resource):
        @namespace.doc(f'get_{_snake_case(base_clazz)}_status')
        def get(self, celery_task_id: str):
            """
            Get the status of Celery Async Task
            """
            return _get_celery_status(celery_task_id, celery_application)


def _snake_case(name: str) -> str:
    s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
    return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()
