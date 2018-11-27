import unittest

from flask import Flask
from flask_restplus import Api, Resource
from pycommon_test.service_tester import JSONTestCase

from pycommon_server.celery_common import AsyncNamespaceProxy, _snake_case, how_to_get_celery_status
from pycommon_server.flask_restplus_common import successful_model


class CeleryTaskStub:
    id = 'idtest'


class AsyncRouteTest(JSONTestCase):

    def create_app(self):
        app = Flask(__name__)
        app.config['TESTING'] = True
        self.api = Api(app)

        return app

    def test_aysnc_ns_proxy_should_create_2extra_endpoints(self):
        namespace = AsyncNamespaceProxy(
            self.api.namespace('Test Namespace', path='/foo', description='Test namespace operations'), None, {})

        @namespace.async_route('/bar', successful_model)
        class TestEndpoint(Resource):
            pass

        ## contains 2 namespace : / and /foo
        self.assertEqual(2, len(self.api.namespaces))
        ## Test will check only our ns
        ns = self.api.namespaces[1]
        self.assertEqual(3, len(ns.resources))
        regular_endpoint = ns.resources[0]
        self.assertEqual('/bar', regular_endpoint[1][0])
        self.assertEqual(TestEndpoint, regular_endpoint[0])
        result_endpoint = ns.resources[1]
        self.assertEqual('/bar/result/<string:celery_task_id>', result_endpoint[1][0])
        status_endpoint = ns.resources[2]
        self.assertEqual('/bar/status/<string:celery_task_id>', status_endpoint[1][0])


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
        response = how_to_get_celery_status(celery_task)
        self.assertEqual('http://localhost/status/idtest', response.headers['location'])
        self.assertEqual(b'Computation status can be found using this URL: http://localhost/status/idtest',
                         response.data)
        print(response)
