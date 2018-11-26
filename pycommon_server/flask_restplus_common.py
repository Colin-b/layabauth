import inspect
import logging
import os
import sys
import time
import traceback
from collections import OrderedDict
from functools import wraps
from http import HTTPStatus
from typing import List

import flask
from flask import request, has_request_context, Flask
from flask_compress import Compress
from flask_cors import CORS
from flask_restplus import Resource, fields, Api
from werkzeug.exceptions import Unauthorized

logger = logging.getLogger(__name__)


def add_monitoring_namespace(api, error_responses, health_controller):
    """
    Create a monitoring namespace containing the Health check endpoint.
    :param api: The root Api
    :param error_responses: All Flask RestPlus error responses (usually the return call from pycommon_error.add_error_handlers)
    :param health_controller: The Health controller (usually located into controllers.Health)
    :return: The monitoring namespace (you can use it to add additional endpoints)
    """
    namespace = api.namespace('monitoring', path='/', description='Monitoring operations')
    health_controller.namespace(namespace)

    @namespace.route('/health')
    @namespace.doc(**error_responses)
    class Health(Resource):

        @namespace.marshal_with(health_controller.get_response_model, description='Server is in a coherent state.')
        def get(self):
            """
            Check service health.
            This endpoint perform a quick server state check.
            """
            # TODO follow https://inadarei.github.io/rfc-healthcheck/
            return health_controller.get()

    return namespace


successful_return = {'status': 'Successful'}, HTTPStatus.OK


def successful_model(api):
    return api.model('Successful', {'status': fields.String(default='Successful')})


successful_deletion_return = '', HTTPStatus.NO_CONTENT
successful_deletion_response = HTTPStatus.NO_CONTENT, 'Sample deleted'


class User:
    def __init__(self, decoded_body: dict):
        import oauth2helper.content
        self.name = oauth2helper.content.user_name(decoded_body)


class Authentication:
    """
    Contains helper to manage authentication.
    """

    @staticmethod
    def authorizations(**scopes) -> dict:
        """
        Return all security definitions.
        Contains only one OAuth2 definition using Engie Azure authentication.

        :param scopes: All scopes that should be available (scope_name = 'description as a string').
        """
        engie_tenant_id = '24139d14-c62c-4c47-8bdd-ce71ea1d50cf'
        nonce = scopes.pop('nonce', '7362CAEA-9CA5-4B43-9BA3-34D7C303EBA7')

        return {
            'oauth2': {
                'scopes': scopes,
                'flow': 'implicit',
                'authorizationUrl': f'https://login.microsoftonline.com/{engie_tenant_id}/oauth2/authorize?nonce={nonce}',
                'type': 'oauth2'
            }
        }

    @staticmethod
    def method_authorizations(*scopes) -> dict:
        """
        Return method security.
        Contains only one OAuth2 security.

        :param scopes: All scope names that should be available (as string).
        """
        return {
            'security': [
                {
                    'oauth2': scopes
                }
            ]
        }

    @staticmethod
    def _to_user(token: str) -> User:
        try:
            from jwt.exceptions import InvalidTokenError, InvalidKeyError
            import oauth2helper.token
            json_header, json_body = oauth2helper.token.validate(token)
            return User(json_body)
        except ImportError:
            raise Unauthorized('Server is missing oauth2helper module to handle authentication.')
        except (InvalidTokenError or InvalidKeyError) as e:
            raise Unauthorized(e.args[0])


def requires_authentication(func):
    @wraps(func)
    def wrapper(*func_args, **func_kwargs):
        authorization = flask.request.headers.get('Authorization')
        token = authorization[7:] if authorization and authorization.startswith('Bearer ') else None
        flask.g.current_user = Authentication._to_user(token)
        return func(*func_args, **func_kwargs)

    return wrapper


class Statistics:
    def __init__(self, func, *func_args, **func_kwargs):
        args_name = list(OrderedDict.fromkeys(inspect.getfullargspec(func)[0] + list(func_kwargs.keys())))
        args_dict = OrderedDict(list(zip(args_name, func_args)) + list(func_kwargs.items()))
        self.stats = {'func_name': '.'.join(func.__qualname__.rsplit('.', 2)[-2:])}
        self.stats.update(args_dict)
        # add request args
        if has_request_context():
            self.stats.update({
                # TODO Explain why the key name should change if v length is not 1
                f'request_args.{k}' if len(v) == 1 else k: v[0] if len(v) == 1 else v
                for k, v in dict(request.args).items()
            })
            self.stats.update({f'request_headers.{k}': v for k, v in dict(request.headers).items()})
        self.start = time.perf_counter()

    def success(self):
        self.stats['request_processing_time'] = time.perf_counter() - self.start
        logger.info(self.stats)

    def exception_occurred(self):
        if has_request_context():
            self.stats['request.data'] = request.data
        exc_type, exc_value, exc_traceback = sys.exc_info()
        trace = traceback.extract_tb(exc_traceback)
        # Do not want the current frame in the traceback
        if len(trace) > 1:
            trace = trace[1:]
        trace.reverse()
        trace_summary = '/'.join([os.path.splitext(os.path.basename(tr.filename))[0] + '.' + tr.name for tr in trace])
        self.stats.update({
            'error.summary': trace_summary,
            'error.class': exc_type.__name__,
            'error.msg': str(exc_value),
            'error.traceback': traceback.format_exc(),
        })
        logger.critical(self.stats)


def _log_request_details(func):
    @wraps(func)
    def wrapper(*func_args, **func_kwargs):
        if "Health.get" in func.__qualname__:
            return func(*func_args, **func_kwargs)

        statistics = Statistics(func, *func_args, **func_kwargs)
        try:
            ret = func(*func_args, **func_kwargs)
            statistics.success()
            return ret
        except Exception:
            statistics.exception_occurred()
            raise

    return wrapper


class ReverseProxied:
    '''
    Wrap the application in this middleware and configure the
    front-end server to add these headers, to let you quietly bind
    this to a URL other than / and to an HTTP scheme that is
    different than what is used locally.

    :param app: the WSGI application
    '''

    def __init__(self, app):
        self.app = app

    def __call__(self, environ, start_response):
        original_url = environ.get('HTTP_X_ORIGINAL_REQUEST_URI', '')
        if original_url:
            script_name = '/' + original_url.split('/', maxsplit=2)[1]
            environ['SCRIPT_NAME'] = script_name

            path_info = environ.get('PATH_INFO', '')
            if path_info.startswith(script_name):
                environ['PATH_INFO'] = path_info[len(script_name):]

            scheme = environ.get('HTTP_X_SCHEME', '')
            if scheme:
                environ['wsgi.url_scheme'] = scheme
        return self.app(environ, start_response)


def create_api(version: str, title: str, cors: bool = True, compress_mimetypes: List[str] = [],
               reverse_proxy: bool = True, **kwargs):
    application = Flask(__name__)

    if cors:
        CORS(application)

    if compress_mimetypes:
        compress = Compress()
        compress.init_app(application)
        application.config['COMPRESS_MIMETYPES'] = compress_mimetypes

    if reverse_proxy:
        application.wsgi_app = ReverseProxied(application.wsgi_app)

    api = Api(
        application,
        version=version,
        title=title,
        **kwargs
    )

    return application, api


Resource.method_decorators.append(_log_request_details)
