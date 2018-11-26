import inspect
import logging
import os
import sys
import time
import traceback
from collections import OrderedDict
from functools import wraps
from http import HTTPStatus
import json
import flask
from flask import request, has_request_context, make_response
from flask_restplus import Resource, fields
from werkzeug.exceptions import Unauthorized

logger = logging.getLogger(__name__)


def add_monitoring_namespace(api, error_responses, health_details):
    """
    Create a monitoring namespace containing the Health check endpoint.
    This endpoint implements https://inadarei.github.io/rfc-healthcheck/

    :param api: The root Api
    :param error_responses: All Flask RestPlus error responses (usually the return call from pycommon_error.add_error_handlers)
    :param health_details: Function returning a tuple with 3 dictionaries: pass details, warn details and error details
    :return: The monitoring namespace (you can use it to add additional endpoints)
    """
    namespace = api.namespace('monitoring', path='/', description='Monitoring operations')
    get_response_model = namespace.model('Health', {
        'status': fields.String(description='Indicates whether the service status is acceptable or not.', required=True, example='pass', enum=['pass', 'fail', 'warn']),
        'version': fields.String(description='Public version of the service.', required=True, example='1'),
        'releaseId': fields.String(description='Version of the service.', required=True, example='1.0.0'),
        'details': fields.Raw(description='Provides more details about the status of the service.', required=True),
        'output': fields.String(description='Raw error output.', required=False),
    })

    version = api.version.split('.', maxsplit=1)[0]
    release_id = api.version

    @namespace.route('/health')
    @namespace.doc(**error_responses)
    class Health(Resource):

        @namespace.marshal_with(get_response_model, description='Server is in a coherent state.')
        def get(self):
            """
            Check service health.
            This endpoint perform a quick server state check.
            """
            details = {}
            try:
                pass_details, warn_details, fail_details = health_details()
                details.update(pass_details or {})
                details.update(warn_details or {})
                details.update(fail_details or {})
                if fail_details:
                    return self._send_status('fail', 400, details)
                if warn_details:
                    return self._send_status('warn', 200, details)
                return self._send_status('pass', 200, details)
            except Exception as e:
                return self._send_status('fail', 400, details, output=str(e))

        def _send_status(self, status: str, code: int, details: dict, **kwargs):
            body = {
                'status': status,
                'version': version,
                'releaseId': release_id,
                'details': details,
            }
            body.update(kwargs)
            response = make_response(json.dumps(body), code)
            response.headers['Content-Type'] = 'application/health+json'
            return response

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


Resource.method_decorators.append(_log_request_details)
