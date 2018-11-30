import unittest

import flask
from flask import Flask
from flask_restplus import Api, Resource, fields
from pycommon_test.celery_mock import TestCeleryAppProxy
from pycommon_test.service_tester import JSONTestCase

from pycommon_server.celery_common import AsyncNamespaceProxy, _snake_case, how_to_get_celery_status, \
    build_celery_application


class CeleryTaskStub:
    id = 'idtest'


def successful_model(api):
    return api.model('Successful', {'status': fields.String(default='Successful')})


class AsyncRouteTest(JSONTestCase):

    def create_app(self):
        app = Flask(__name__)
        app.config['TESTING'] = True
        app.config['DEBUG'] = True
        self.api = Api(app)
        config = {'celery': {'namespace': 'test-celery', 'broker': 'memory://localhost/',
                             'backend': 'memory://localhost/'}}
        celery_application = TestCeleryAppProxy(build_celery_application(config))

        ns = AsyncNamespaceProxy(
            self.api.namespace('Test Namespace', path='/foo', description='Test namespace operations'),
            celery_application, {})

        @ns.async_route('/bar', successful_model(self.api))
        class TestEndpoint(Resource):
            def get(self):
                @celery_application.task(queue=celery_application.namespace)
                def fetch_the_answer():
                    return {"status": "why not", "foo": "bar"}

                celery_task = fetch_the_answer.apply_async()
                return how_to_get_celery_status(celery_task)

        return app

    def test_aysnc_ns_proxy_should_create_2extra_endpoints(self):
        response = self.client.get('/swagger.json')
        self.assert200(response)
        self.assert_swagger(response, {
            'swagger': '2.0',
            'basePath': '/',
            'paths': {
                '/foo/bar': {
                    'get': {'responses': {'200': {'description': 'Success'}}, 'operationId': 'get_test_endpoint',
                            'tags': ['Test Namespace']}},
                '/foo/bar/result/{celery_task_id}': {
                    'parameters': [{'name': 'celery_task_id', 'in': 'path', 'required': True, 'type': 'string'}],
                    'get': {
                        'responses': {
                            '200': {'description': 'Success', 'schema': {'$ref': '#/definitions/Successful'}}},
                        'summary': 'Query the result of Celery Async Task', 'operationId': 'get_test_endpoint_result',
                        'parameters': [{'name': 'X-Fields', 'in': 'header', 'type': 'string', 'format': 'mask',
                                        'description': 'An optional fields mask'}], 'tags': ['Test Namespace']}},
                '/foo/bar/status/{celery_task_id}': {
                    'parameters': [{'name': 'celery_task_id', 'in': 'path', 'required': True, 'type': 'string'}],
                    'get': {'responses': {'200': {'description': 'Success'}},
                            'summary': 'Get the status of Celery Async Task',
                            'operationId': 'get_test_endpoint_status', 'tags': ['Test Namespace']}}},
            'info': {'title': 'API', 'version': '1.0'},
            'produces': ['application/json'],
            'consumes': ['application/json'],
            'tags': [{'name': 'Test Namespace', 'description': 'Test namespace operations'}],
            'definitions': {'Successful': {'properties': {'status': {'type': 'string', 'default': 'Successful'}},
                                           'type': 'object'}},
            'responses': {'ParseError': {'description': "When a mask can't be parsed"},
                          'MaskError': {'description': 'When any error occurs on mask'}}
        })

    def test_aysnc_call_task(self):
        response = self.client.get('/foo/bar')
        status_url = response.headers['location'].replace('http://localhost', '')
        status_reply = self.client.get(status_url)
        result_url = status_reply.location.replace('http://localhost', '')
        result_reply = self.client.get(result_url)
        self.assert_json(result_reply, {"status": "why not"})

    def test_aysnc_call_task_without_endpoint_call(self):
        status_reply = self.client.get('/foo/bar/status/42')
        self.assert_json(status_reply, {"state": "PENDING"})

class TestSnakeCase(unittest.TestCase):

    def test_camel_case_to_snake_case(self):
        snaked_string = _snake_case('TestMe')
        self.assertEqual('test_me', snaked_string)

    def test_snake_case_withoutunderscore(self):
        snaked_string = _snake_case('testme')
        self.assertEqual('testme', snaked_string)

    def test_malformed_camel(self):
        with self.assertRaises(ValueError) as context:
            _snake_case('Test_Me')
        self.assertTrue('Test_Me should be Camel Case and should not contain any _' in str(context.exception))


class TestGetCeleryStatus(JSONTestCase):

    def create_app(self):
        app = Flask(__name__)
        app.config['TESTING'] = True
        self.api = Api(app)

        return app

    def test_get_celery_status(self):
        celery_task = CeleryTaskStub()
        flask.request.base_url = 'http://localhost/foo'
        response = how_to_get_celery_status(celery_task)
        self.assertEqual('http://localhost/foo/status/idtest', response.headers['location'])
        self.assertEqual(b'Computation status can be found using this URL: http://localhost/foo/status/idtest',
                         response.data)
        print(response)
