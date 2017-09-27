from flask_restplus import Resource, fields


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
    @api.marshal_with(exception_model, code=400)
    def handle_exception(exception):
        """This is the default error handling."""
        return {'message': str(exception)}, 400

    return 400, 'An unexpected error occurred.', exception_model


def add_monitoring_namespace(api, exception_response, health_controller):
    """
    Create a monitoring namespace containing the Health check endpoint.

    :param api: The root Api
    :param exception_response: A Flask RestPlus response (usually the return call from add_exception_handler)
    :param health_controller: The Health controller (usually located into controllers.Health)
    :return: The monitoring namespace (you can use it to add additional endpoints)
    """
    monitoring_ns = api.namespace('monitoring', path='/', description='Monitoring operations')

    @monitoring_ns.route('/health')
    class Health(Resource):

        @monitoring_ns.marshal_with(health_controller.marshaller(monitoring_ns))
        @monitoring_ns.response(*exception_response)
        def get(self):
            """
            Check service health.
            This endpoint is called at regular interval by Consul to check service health.
            """
            return health_controller().get()

    return monitoring_ns


successful_return = {'status': 'Successful'}, 200


def successful_model(api):
    return api.model('Successful', {'status': fields.String(default='Successful')})


successful_deletion_return = '', 204
successful_deletion_response = 204, 'Sample deleted'
