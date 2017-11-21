import logging
from flask_restplus import Resource, fields
import time
from collections import OrderedDict
import inspect
import sys
import traceback
import os


logger = logging.getLogger(__name__)


def _exception_model(api):
    exception_details = {
        'message': fields.String(description='Description of the error.',
                                 required=True,
                                 example='This is a description of the error.')
    }
    return api.model('Exception', exception_details)


def add_exception_handler(api):
    """
    Add the default Exception handler.

    :param api: The root Api
    """
    exception_model = _exception_model(api)

    @api.errorhandler(Exception)
    @api.marshal_with(exception_model, code=500)
    def handle_exception(exception):
        """This is the default error handling."""
        logger.exception('An unexpected error occurred.')
        return {'message': str(exception)}, 500

    return 500, 'An unexpected error occurred.', exception_model


def add_monitoring_namespace(api, exception_response, health_controller):
    """
    Create a monitoring namespace containing the Health check endpoint.

    :param api: The root Api
    :param exception_response: A Flask RestPlus response (usually the return call from add_exception_handler)
    :param health_controller: The Health controller (usually located into controllers.Health)
    :return: The monitoring namespace (you can use it to add additional endpoints)
    """
    monitoring_ns = api.namespace('monitoring', path='/', description='Monitoring operations')
    health_controller.namespace(monitoring_ns)

    @monitoring_ns.route('/health')
    class Health(Resource):

        @monitoring_ns.marshal_with(health_controller.get_response_model, description='Server is in a coherent state.')
        @monitoring_ns.response(*exception_response)
        def get(self):
            """
            Check service health.
            This endpoint perform a quick server state check.
            """
            return health_controller().get()

    return monitoring_ns


successful_return = {'status': 'Successful'}, 200


def successful_model(api):
    return api.model('Successful', {'status': fields.String(default='Successful')})


successful_deletion_return = '', 204
successful_deletion_response = 204, 'Sample deleted'


class LogRequestDetails:
    """
    Decorator for incoming requests.
    """
    def __init__(self, request_method):
        self.request_method = request_method
        self.log = "Health.get" not in request_method.__qualname__

    def __call__(self, *func_args, **func_kwargs):
        from flask import request, has_request_context
        if not self.log:
            return self.request_method(*func_args, **func_kwargs)
        else:
            args_name = list(OrderedDict.fromkeys(inspect.getfullargspec(self.request_method)[0] + list(func_kwargs.keys())))
            args_dict = OrderedDict(list(zip(args_name, func_args)) + list(func_kwargs.items()))
            stats = {'func_name': '.'.join(self.request_method.__qualname__.rsplit('.',2)[-2:])}
            stats.update(args_dict)
            # add request args
            if has_request_context():
                stats.update(dict([(f'request.args.{k}', v[0]) if len(v) == 1 else (k, v) for k, v in dict(request.args).items()]))
                stats.update({f'request.headers.{k}':v for k,v in dict(request.headers).items()})
            start = time.perf_counter()
            try:
                ret =  self.request_method(*func_args, **func_kwargs)
            except Exception as e:
                if has_request_context():
                    stats['request.data'] = request.data
                exc_type, exc_value, exc_traceback = sys.exc_info()
                trace = traceback.extract_tb(exc_traceback)
                #don't want the current frame in the traceback
                if len(trace) > 1:
                    trace = trace[1:]
                trace.reverse()
                trace_summary = '/'.join([os.path.splitext(os.path.basename(tr.filename))[0]+'.'+tr.name for tr in trace])
                tb = [{'line':tr.line,'file': tr.filename, 'lineno':tr.lineno, 'func':tr.name} for tr in trace]
                stats.update({'error.summary':trace_summary, 'error.class':exc_type.__name__, 'error.msg':str(exc_value), 'error.traceback':traceback.format_exc()})
                logger.critical(stats)
                raise e

            stats['request.processing_time'] = time.perf_counter() - start
            logger.info(stats)
            return ret


# This will log every incoming request (do not use a method to avoid registering it twice by accident)
Resource.method_decorators.append(LogRequestDetails)

