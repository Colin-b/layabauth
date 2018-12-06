import flask
from flask import Flask, make_response
from flask_restplus import Api, Resource, fields
from pycommon_test.celery_mock import TestCeleryAppProxy
from pycommon_test.service_tester import JSONTestCase

from pycommon_server.celery_common import (
    AsyncNamespaceProxy,
    how_to_get_async_status,
    build_celery_application,
    how_to_get_async_status_doc
)


class AsyncRouteTest(JSONTestCase):

    def create_app(self):
        app = Flask(__name__)
        app.config['TESTING'] = True
        app.config['DEBUG'] = True
        self.api = Api(app)
        config = {'celery': {'namespace': 'test-celery', 'broker': 'memory://localhost/',
                             'backend': 'memory://localhost/'}}
        celery_application = TestCeleryAppProxy(build_celery_application(config))

        ns = AsyncNamespaceProxy(self.api.namespace('Test space', path='/foo', description='Test'), celery_application)

        @ns.async_route('/bar', serializer=self.api.model('BarModel', {'status': fields.String, 'foo': fields.String}))
        class TestEndpoint(Resource):
            @ns.doc(**how_to_get_async_status_doc)
            def get(self):
                @celery_application.task(queue=celery_application.namespace)
                def fetch_the_answer():
                    return {"status": "why not", "foo": "bar"}

                celery_task = fetch_the_answer.apply_async()
                return how_to_get_async_status(celery_task)

        @ns.async_route('/bar2',
                        [self.api.model('Bar2Model', {'status2': fields.String, 'foo2': fields.String})])
        class TestEndpoint2(Resource):
            @ns.doc(**how_to_get_async_status_doc)
            def get(self):
                @celery_application.task(queue=celery_application.namespace)
                def fetch_the_answer():
                    return [{"status2": "why not2", "foo2": "bar2"}]

                celery_task = fetch_the_answer.apply_async()
                return how_to_get_async_status(celery_task)

        @ns.async_route('/csv')
        class TestEndpointNoSerialization(Resource):
            @ns.doc(**how_to_get_async_status_doc)
            def get(self):
                @celery_application.task(queue=celery_application.namespace)
                def fetch_the_answer():
                    return make_response("a;b;c", 200, {"Content-type": "text/csv"})

                celery_task = fetch_the_answer.apply_async()
                return how_to_get_async_status(celery_task)

        return app

    def test_async_ns_proxy_should_create_2_extra_endpoints(self):
        response = self.client.get('/swagger.json')
        self.assert200(response)
        self.assert_swagger(response, {'swagger': '2.0', 'basePath': '/', 'paths': {'/foo/bar': {'get': {'responses': {
            '202': {'description': 'Computation started.', 'schema': {'type': 'string'}, 'headers': {
                'location': {'description': 'URL to fetch computation status from.', 'type': 'string'}}}},
            'operationId': 'get_test_endpoint',
            'tags': [
                'Test space']}},
            '/foo/bar/result/{task_id}': {
                'parameters': [
                    {'name': 'task_id',
                     'in': 'path',
                     'required': True,
                     'type': 'string'}],
                'get': {'responses': {'200': {
                    'description': 'Success',
                    'schema': {
                        '$ref': '#/definitions/BarModel'}}},
                    'summary': 'Retrieve result for provided task',
                    'operationId': 'get_test_endpoint_result',
                    'parameters': [
                        {'name': 'X-Fields',
                         'in': 'header',
                         'type': 'string',
                         'format': 'mask',
                         'description': 'An optional fields mask'}],
                    'tags': [
                        'Test space']}},
            '/foo/bar/status/{task_id}': {
                'parameters': [
                    {'name': 'task_id',
                     'in': 'path',
                     'required': True,
                     'type': 'string'}],
                'get': {'responses': {'200': {
                    'description': 'Task is still computing.',
                    'schema': {
                        '$ref': '#/definitions/CurrentAsyncState'}},
                    '303': {
                        'description': 'Result is available.',
                        'headers': {
                            'location': {
                                'description': 'URL to fetch results from.',
                                'type': 'string'}}},
                    '500': {
                        'description': 'An unexpected error occurred.',
                        'schema': {
                            'type': 'string',
                            'description': 'Stack trace.'}}},
                    'summary': 'Retrieve status for provided task',
                    'operationId': 'get_test_endpoint_status',
                    'tags': [
                        'Test space']}},
            '/foo/bar2': {'get': {'responses': {
                '202': {
                    'description': 'Computation started.',
                    'schema': {
                        'type': 'string'},
                    'headers': {'location': {
                        'description': 'URL to fetch computation status from.',
                        'type': 'string'}}}},
                'operationId': 'get_test_endpoint2',
                'tags': [
                    'Test space']}},
            '/foo/bar2/result/{task_id}': {
                'parameters': [
                    {'name': 'task_id',
                     'in': 'path',
                     'required': True,
                     'type': 'string'}],
                'get': {'responses': {'200': {
                    'description': 'Success',
                    'schema': {'type': 'array',
                               'items': {
                                   '$ref': '#/definitions/Bar2Model'}}}},
                    'summary': 'Retrieve result for provided task',
                    'operationId': 'get_test_endpoint2_result',
                    'parameters': [
                        {'name': 'X-Fields',
                         'in': 'header',
                         'type': 'string',
                         'format': 'mask',
                         'description': 'An optional fields mask'}],
                    'tags': [
                        'Test space']}},
            '/foo/bar2/status/{task_id}': {
                'parameters': [
                    {'name': 'task_id',
                     'in': 'path',
                     'required': True,
                     'type': 'string'}],
                'get': {'responses': {'200': {
                    'description': 'Task is still computing.',
                    'schema': {
                        '$ref': '#/definitions/CurrentAsyncState'}},
                    '303': {
                        'description': 'Result is available.',
                        'headers': {
                            'location': {
                                'description': 'URL to fetch results from.',
                                'type': 'string'}}},
                    '500': {
                        'description': 'An unexpected error occurred.',
                        'schema': {
                            'type': 'string',
                            'description': 'Stack trace.'}}},
                    'summary': 'Retrieve status for provided task',
                    'operationId': 'get_test_endpoint2_status',
                    'tags': [
                        'Test space']}},
            '/foo/csv': {'get': {'responses': {
                '202': {
                    'description': 'Computation started.',
                    'schema': {
                        'type': 'string'},
                    'headers': {'location': {
                        'description': 'URL to fetch computation status from.',
                        'type': 'string'}}}},
                'operationId': 'get_test_endpoint_no_serialization',
                'tags': [
                    'Test space']}},
            '/foo/csv/result/{task_id}': {
                'parameters': [
                    {'name': 'task_id',
                     'in': 'path',
                     'required': True,
                     'type': 'string'}],
                'get': {'responses': {'200': {
                    'description': 'Success'}},
                    'summary': 'Retrieve result for provided task',
                    'operationId': 'get_test_endpoint_no_serialization_result',
                    'tags': [
                        'Test space']}},
            '/foo/csv/status/{task_id}': {
                'parameters': [
                    {'name': 'task_id',
                     'in': 'path',
                     'required': True,
                     'type': 'string'}],
                'get': {'responses': {'200': {
                    'description': 'Task is still computing.',
                    'schema': {
                        '$ref': '#/definitions/CurrentAsyncState'}},
                    '303': {
                        'description': 'Result is available.',
                        'headers': {
                            'location': {
                                'description': 'URL to fetch results from.',
                                'type': 'string'}}},
                    '500': {
                        'description': 'An unexpected error occurred.',
                        'schema': {
                            'type': 'string',
                            'description': 'Stack trace.'}}},
                    'summary': 'Retrieve status for provided task',
                    'operationId': 'get_test_endpoint_no_serialization_status',
                    'tags': [
                        'Test space']}}},
                                       'info': {'title': 'API', 'version': '1.0'}, 'produces': ['application/json'],
                                       'consumes': ['application/json'],
                                       'tags': [{'name': 'Test space', 'description': 'Test'}], 'definitions': {
                'BarModel': {'properties': {'status': {'type': 'string'}, 'foo': {'type': 'string'}}, 'type': 'object'},
                'CurrentAsyncState': {'required': ['state'], 'properties': {
                    'state': {'type': 'string', 'description': 'Indicates current computation state.',
                              'example': 'PENDING'}}, 'type': 'object'},
                'Bar2Model': {'properties': {'status2': {'type': 'string'}, 'foo2': {'type': 'string'}},
                              'type': 'object'}},
                                       'responses': {'ParseError': {'description': "When a mask can't be parsed"},
                                                     'MaskError': {'description': 'When any error occurs on mask'}}})

    def test_async_call_task(self):
        response = self.client.get('/foo/bar')
        status_url = self.assert_202_regex(response, '/foo/bar/status/.*')
        self.assert_text_regex(response,
                               'Computation status can be found using this URL: http://localhost/foo/bar/status/.*')
        status_reply = self.client.get(status_url)
        result_url = self.assert_303_regex(status_reply, '/foo/bar/result/.*')
        result_reply = self.client.get(result_url)
        self.assert200(result_reply)
        self.assert_json(result_reply, {"status": "why not", "foo": "bar"})

        response = self.client.get('/foo/bar2')
        status_url = self.assert_202_regex(response, '/foo/bar2/status/.*')
        self.assert_text_regex(response,
                               'Computation status can be found using this URL: http://localhost/foo/bar2/status/.*')
        status_reply = self.client.get(status_url)
        result_url = self.assert_303_regex(status_reply, '/foo/bar2/result/.*')
        result_reply = self.client.get(result_url)
        self.assert200(result_reply)
        self.assert_json(result_reply, [{"status2": "why not2", "foo2": "bar2"}])

    def test_async_call_task_without_endpoint_call(self):
        status_reply = self.client.get('/foo/bar/status/42')
        self.assertStatus(status_reply, 200)
        self.assert_json(status_reply, {"state": "PENDING"})

    def test_async_call_without_serialization(self):
        response = self.client.get('/foo/csv')
        status_url = self.assert_202_regex(response, '/foo/csv/status/.*')
        self.assert_text_regex(response,
                               'Computation status can be found using this URL: http://localhost/foo/csv/status/.*')
        status_reply = self.client.get(status_url)
        result_url = self.assert_303_regex(status_reply, '/foo/csv/result/.*')
        result_reply = self.client.get(result_url)
        self.assert200(result_reply)
        self.assertEqual(result_reply.data.decode(), "a;b;c")


class TestGetCeleryStatus(JSONTestCase):

    def create_app(self):
        app = Flask(__name__)
        app.config['TESTING'] = True
        return app

    def test_get_async_status(self):
        class CeleryTaskStub:
            id = 'idtest'

        celery_task = CeleryTaskStub()
        flask.request.base_url = 'http://localhost/foo'
        response = how_to_get_async_status(celery_task)
        self.assert_202_regex(response, '/foo/status/idtest')
        self.assert_text(response, 'Computation status can be found using this URL: http://localhost/foo/status/idtest')
