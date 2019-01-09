import gzip
import logging
import os
import os.path
import tempfile
import unittest
from unittest.mock import Mock

import responses
from flask import Flask, Response, json
from flask_restplus import Resource, Api
from pycommon_test import mock_now, revert_now
from pycommon_test.samba_mock import TestConnection
from pycommon_test.service_tester import JSONTestCase

from pycommon_server import flask_restplus_common, logging_filter, windows, health
from pycommon_server.configuration import load_configuration, load_logging_configuration, load

logger = logging.getLogger(__name__)


def _add_file(folder: str, file_name: str, *lines) -> None:
    with open(os.path.join(folder, file_name), 'w') as config_file:
        config_file.writelines('\n'.join(lines))


def _add_dir(parent_folder: str, folder: str) -> str:
    folder_path = os.path.join(parent_folder, folder)
    os.makedirs(os.path.join(parent_folder, folder))
    return folder_path


class ConfigurationTest(unittest.TestCase):

    def setUp(self):
        logger.info(f'-------------------------------')
        logger.info(f'Start of {self._testMethodName}')
        os.environ.pop('SERVER_ENVIRONMENT', None)

    def tearDown(self):
        logger.info(f'End of {self._testMethodName}')
        logger.info(f'-------------------------------')

    def test_empty_configuration_if_file_not_found(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            self.assertEqual({}, load_configuration(tmp_dir))

    def test_default_configuration_loaded_if_no_environment_specified(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            _add_file(tmp_dir, 'configuration_default.yml', 'section_default:', '  key: value')
            self.assertEqual(
                {
                    'section_default': {
                        'key': 'value'
                    }
                },
                load_configuration(tmp_dir))

    def test_server_environment_configuration_loaded(self):
        os.environ['SERVER_ENVIRONMENT'] = 'test'
        with tempfile.TemporaryDirectory() as tmp_dir:
            _add_file(tmp_dir, 'configuration_test.yml', 'section_test:', '  key: value')
            self.assertEqual(
                {
                    'section_test': {
                        'key': 'value'
                    }
                },
                load_configuration(tmp_dir))

    def test_hardcoded_default_logging_configuration_if_file_not_found(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            self.assertIsNone(load_logging_configuration(tmp_dir))

    def test_default_logging_configuration_loaded_if_no_environment_specified(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            _add_file(tmp_dir, 'logging_default.yml',
                      'version: 1',
                      'formatters:',
                      '  clean:',
                      "    format: '%(message)s'",
                      'handlers:',
                      '  standard_output:',
                      '    class: logging.StreamHandler',
                      '    formatter: clean',
                      '    stream: ext://sys.stdout',
                      'root:',
                      '  level: INFO',
                      '  handlers: [standard_output]')
            self.assertEqual(os.path.join(tmp_dir, 'logging_default.yml'), load_logging_configuration(tmp_dir))

    def test_server_environment_logging_configuration_loaded(self):
        os.environ['SERVER_ENVIRONMENT'] = 'test'
        with tempfile.TemporaryDirectory() as tmp_dir:
            _add_file(tmp_dir, 'logging_test.yml',
                      'version: 1',
                      'formatters:',
                      '  clean:',
                      "    format: '%(message)s'",
                      'handlers:',
                      '  standard_output:',
                      '    class: logging.StreamHandler',
                      '    formatter: clean',
                      '    stream: ext://sys.stdout',
                      'root:',
                      '  level: INFO',
                      '  handlers: [standard_output]')
            self.assertEqual(os.path.join(tmp_dir, 'logging_test.yml'), load_logging_configuration(tmp_dir))

    def test_all_default_environment_configurations_loaded(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            configuration_folder = _add_dir(tmp_dir, 'configuration')
            server_folder = _add_dir(tmp_dir, 'my_server')
            _add_file(configuration_folder, 'configuration_default.yml', 'section_test:', '  key: value')
            _add_file(configuration_folder, 'logging_default.yml',
                      'version: 1',
                      'formatters:',
                      '  clean:',
                      "    format: '%(message)s'",
                      'handlers:',
                      '  standard_output:',
                      '    class: logging.StreamHandler',
                      '    formatter: clean',
                      '    stream: ext://sys.stdout',
                      'root:',
                      '  level: INFO',
                      '  handlers: [standard_output]')
            self.assertEqual(
                {
                    'section_test': {
                        'key': 'value'
                    }
                },
                load(os.path.join(server_folder, 'server.py')))

    def test_all_server_environment_configurations_loaded(self):
        os.environ['SERVER_ENVIRONMENT'] = 'test'
        with tempfile.TemporaryDirectory() as tmp_dir:
            configuration_folder = _add_dir(tmp_dir, 'configuration')
            server_folder = _add_dir(tmp_dir, 'my_server')
            _add_file(configuration_folder, 'configuration_test.yml', 'section_test:', '  key: value')
            _add_file(configuration_folder, 'logging_test.yml',
                      'version: 1',
                      'formatters:',
                      '  clean:',
                      "    format: '%(message)s'",
                      'handlers:',
                      '  standard_output:',
                      '    class: logging.StreamHandler',
                      '    formatter: clean',
                      '    stream: ext://sys.stdout',
                      'root:',
                      '  level: INFO',
                      '  handlers: [standard_output]')
            self.assertEqual(
                {
                    'section_test': {
                        'key': 'value'
                    }
                },
                load(os.path.join(server_folder, 'server.py')))


class HealthCheckWithException(JSONTestCase):
    def create_app(self):
        app = Flask(__name__)
        app.testing = True
        api = Api(app, version='3.2.1')

        def throw_exception():
            raise Exception('This is the error message.')

        flask_restplus_common.add_monitoring_namespace(api, throw_exception)

        return app

    def test_health_check_response_on_exception(self):
        response = self.client.get('/health')
        self.assert400(response)
        self.assert_json(response, {
            'details': {},
            'output': 'This is the error message.',
            'releaseId': '3.2.1',
            'status': 'fail',
            'version': '3',
        })


class HealthCheckWithoutFailureDetails(JSONTestCase):
    def create_app(self):
        app = Flask(__name__)
        app.testing = True
        api = Api(app, version='3.2.1')

        def failure_details():
            return 'fail', None

        flask_restplus_common.add_monitoring_namespace(api, failure_details)

        return app

    def test_health_check_response_on_exception(self):
        response = self.client.get('/health')
        self.assert400(response)
        self.assert_json(response, {
            'details': None,
            'releaseId': '3.2.1',
            'status': 'fail',
            'version': '3',
        })


class HealthCheckWithFailureDetails(JSONTestCase):
    def create_app(self):
        app = Flask(__name__)
        app.testing = True
        api = Api(app, version='3.2.1')

        def failure_details():
            return 'fail', {'toto': {'status': 'warn'}, 'toto2': {'status': 'fail'}}

        flask_restplus_common.add_monitoring_namespace(api, failure_details)

        return app

    def test_health_check_response_on_exception(self):
        response = self.client.get('/health')
        self.assert400(response)
        self.assert_json(response, {
            'details': {'toto': {'status': 'warn'}, 'toto2': {'status': 'fail'}},
            'releaseId': '3.2.1',
            'status': 'fail',
            'version': '3',
        })


class HealthCheckWithWarnDetails(JSONTestCase):
    def create_app(self):
        app = Flask(__name__)
        app.testing = True
        api = Api(app, version='3.2.1')

        def warning_details():
            return 'warn', {'toto2': {'status': 'pass'}, 'toto': {'status': 'warn'}}

        flask_restplus_common.add_monitoring_namespace(api, warning_details)

        return app

    def test_health_check_response_on_warning(self):
        response = self.client.get('/health')
        self.assert200(response)
        self.assert_json(response, {
            'details': {'toto2': {'status': 'pass'}, 'toto': {'status': 'warn'}},
            'releaseId': '3.2.1',
            'status': 'warn',
            'version': '3',
        })


class HealthCheckWithPassDetails(JSONTestCase):
    def create_app(self):
        app = Flask(__name__)
        app.testing = True
        api = Api(app, version='3.2.1')

        def pass_details():
            return 'pass', {'toto2': {'status': 'pass'}}

        flask_restplus_common.add_monitoring_namespace(api, pass_details)

        return app

    def test_health_check_response_on_pass(self):
        response = self.client.get('/health')
        self.assert200(response)
        self.assert_json(response, {
            'details': {'toto2': {'status': 'pass'}},
            'releaseId': '3.2.1',
            'status': 'pass',
            'version': '3',
        })

    def test_generated_swagger(self):
        response = self.client.get('/swagger.json')
        self.assert200(response)
        self.assert_swagger(response, {'swagger': '2.0', 'basePath': '/', 'paths': {'/health': {'get': {'responses': {
            '200': {'description': 'Server is in a coherent state.', 'schema': {'$ref': '#/definitions/HealthPass'}},
            '400': {'description': 'Server is not in a coherent state.',
                    'schema': {'$ref': '#/definitions/HealthFail'}}}, 'summary': 'Check service health',
            'description': 'This endpoint perform a quick server state check.',
            'operationId': 'get_health',
            'tags': [
                'Monitoring']}}},
                                       'info': {'title': 'API', 'version': '3.2.1'}, 'produces': ['application/json'],
                                       'consumes': ['application/json'],
                                       'tags': [{'name': 'Monitoring', 'description': 'Monitoring operations'}],
                                       'definitions': {
                                           'HealthPass': {'required': ['details', 'releaseId', 'status', 'version'],
                                                          'properties': {'status': {'type': 'string',
                                                                                    'description': 'Indicates whether the service status is acceptable or not.',
                                                                                    'example': 'pass',
                                                                                    'enum': ['pass', 'warn']},
                                                                         'version': {'type': 'string',
                                                                                     'description': 'Public version of the service.',
                                                                                     'example': '1'},
                                                                         'releaseId': {'type': 'string',
                                                                                       'description': 'Version of the service.',
                                                                                       'example': '1.0.0'},
                                                                         'details': {'type': 'object',
                                                                                     'description': 'Provides more details about the status of the service.'}},
                                                          'type': 'object'},
                                           'HealthFail': {'required': ['details', 'releaseId', 'status', 'version'],
                                                          'properties': {'status': {'type': 'string',
                                                                                    'description': 'Indicates whether the service status is acceptable or not.',
                                                                                    'example': 'fail',
                                                                                    'enum': ['fail']},
                                                                         'version': {'type': 'string',
                                                                                     'description': 'Public version of the service.',
                                                                                     'example': '1'},
                                                                         'releaseId': {'type': 'string',
                                                                                       'description': 'Version of the service.',
                                                                                       'example': '1.0.0'},
                                                                         'details': {'type': 'object',
                                                                                     'description': 'Provides more details about the status of the service.'},
                                                                         'output': {'type': 'string',
                                                                                    'description': 'Raw error output.'}},
                                                          'type': 'object'}},
                                       'responses': {'ParseError': {'description': "When a mask can't be parsed"},
                                                     'MaskError': {'description': 'When any error occurs on mask'}}})


class FlaskRestPlusTest(JSONTestCase):
    def create_app(self):
        app = Flask(__name__)
        app.testing = True
        api = Api(app)

        @api.route('/requires_authentication')
        class RequiresAuthentication(Resource):
            @flask_restplus_common.requires_authentication
            def get(self):
                return ''

            @flask_restplus_common.requires_authentication
            def post(self):
                return ''

            @flask_restplus_common.requires_authentication
            def put(self):
                return ''

            @flask_restplus_common.requires_authentication
            def delete(self):
                return ''

        @api.route('/logging')
        class Logging(Resource):
            @flask_restplus_common._log_request_details
            def get(self):
                return ''

            @flask_restplus_common._log_request_details
            def post(self):
                return ''

            @flask_restplus_common._log_request_details
            def put(self):
                return ''

            @flask_restplus_common._log_request_details
            def delete(self):
                return ''

        @api.route('/standard_responses')
        class StandardResponses(Resource):
            @api.doc(**flask_restplus_common.created_response_doc(api))
            def post(self):
                return flask_restplus_common.created_response('/standard_responses?id=42')

            @api.doc(**flask_restplus_common.updated_response_doc(api))
            def put(self):
                return flask_restplus_common.updated_response('/standard_responses?id=43')

            @api.response(*flask_restplus_common.deleted_response_doc)
            def delete(self):
                return flask_restplus_common.deleted_response

        return app

    def test_standard_post_response_without_reverse_proxy(self):
        response = self.post_json('/standard_responses', {})
        self.assertStatus(response, 201)
        self.assert_json(response, {'status': 'Successful'})
        self.assertEqual(response.headers['location'], 'http://localhost/standard_responses?id=42')

    def test_standard_post_response_with_reverse_proxy(self):
        response = self.post_json('/standard_responses', {}, headers={
            'X-Original-Request-Uri': '/reverse/standard_responses',
            'Host': 'localhost',
        })
        self.assertStatus(response, 201)
        self.assert_json(response, {'status': 'Successful'})
        self.assertEqual(response.headers['location'], 'http://localhost/reverse/standard_responses?id=42')

    def test_standard_put_response_without_reverse_proxy(self):
        response = self.put_json('/standard_responses', {})
        self.assertStatus(response, 201)
        self.assert_json(response, {'status': 'Successful'})
        self.assertEqual(response.headers['location'], 'http://localhost/standard_responses?id=43')

    def test_standard_put_response_with_reverse_proxy(self):
        response = self.put_json('/standard_responses', {}, headers={
            'X-Original-Request-Uri': '/reverse/standard_responses',
            'Host': 'localhost',
        })
        self.assertStatus(response, 201)
        self.assert_json(response, {'status': 'Successful'})
        self.assertEqual(response.headers['location'], 'http://localhost/reverse/standard_responses?id=43')

    def test_standard_delete_response(self):
        response = self.client.delete('/standard_responses')
        self.assertStatus(response, 204)

    def test_generated_swagger(self):
        response = self.client.get('/swagger.json')
        self.assert200(response)
        self.assert_swagger(response, {
            'swagger': '2.0', 'basePath': '/', 'paths': {
                '/logging': {
                    'delete': {'responses': {'200': {'description': 'Success'}}, 'operationId': 'delete_logging',
                               'tags': ['default']},
                    'get': {'responses': {'200': {'description': 'Success'}}, 'operationId': 'get_logging',
                            'tags': ['default']},
                    'post': {'responses': {'200': {'description': 'Success'}}, 'operationId': 'post_logging',
                             'tags': ['default']},
                    'put': {'responses': {'200': {'description': 'Success'}}, 'operationId': 'put_logging',
                            'tags': ['default']}
                },
                '/requires_authentication': {
                    'delete': {'responses': {'200': {'description': 'Success'}},
                               'operationId': 'delete_requires_authentication', 'tags': ['default']},
                    'get': {'responses': {'200': {'description': 'Success'}},
                            'operationId': 'get_requires_authentication', 'tags': ['default']},
                    'post': {'responses': {'200': {'description': 'Success'}},
                             'operationId': 'post_requires_authentication', 'tags': ['default']},
                    'put': {'responses': {'200': {'description': 'Success'}},
                            'operationId': 'put_requires_authentication', 'tags': ['default']}
                },
                '/standard_responses': {
                    'delete': {'responses': {'204': {'description': 'Deleted'}},
                               'operationId': 'delete_standard_responses', 'tags': ['default']},
                    'post': {'responses': {'201': {'description': 'Created', 'headers': {
                        'location': {'description': 'Location of created resource.', 'type': 'string'}},
                                                   'schema': {'$ref': '#/definitions/Created'}}},
                             'operationId': 'post_standard_responses', 'tags': ['default']},
                    'put': {'responses': {'201': {'description': 'Updated', 'headers': {
                        'location': {'description': 'Location of updated resource.', 'type': 'string'}},
                                                  'schema': {'$ref': '#/definitions/Updated'}}},
                            'operationId': 'put_standard_responses', 'tags': ['default']}
                }
            },
            'info': {'title': 'API', 'version': '1.0'},
            'produces': ['application/json'],
            'consumes': ['application/json'],
            'tags': [{'name': 'default', 'description': 'Default namespace'}],
            'responses': {
                'ParseError': {'description': "When a mask can't be parsed"},
                'MaskError': {'description': 'When any error occurs on mask'}
            },
            'definitions': {
                'Created': {'properties': {'status': {'default': 'Successful', 'type': 'string'}}, 'type': 'object'},
                'Updated': {'properties': {'status': {'default': 'Successful', 'type': 'string'}}, 'type': 'object'},
            },
        })

    def test_authentication_failure_token_not_provided_on_get(self):
        response = self.client.get('/requires_authentication')
        self.assert401(response)
        self.assert_json(response, {'message': 'JWT Token is mandatory.'})

    def test_authentication_failure_token_not_provided_on_post(self):
        response = self.client.post('/requires_authentication')
        self.assert401(response)
        self.assert_json(response, {'message': 'JWT Token is mandatory.'})

    def test_authentication_failure_token_not_provided_on_put(self):
        response = self.client.put('/requires_authentication')
        self.assert401(response)
        self.assert_json(response, {'message': 'JWT Token is mandatory.'})

    def test_authentication_failure_token_not_provided_on_delete(self):
        response = self.client.delete('/requires_authentication')
        self.assert401(response)
        self.assert_json(response, {'message': 'JWT Token is mandatory.'})

    def test_authentication_failure_fake_token_provided_on_get(self):
        response = self.client.get('/requires_authentication', headers={'Authorization': 'Bearer Fake token'})
        self.assert401(response)
        self.assert_json(response, {
            'message': 'Invalid JWT Token (header, body and signature must be separated by dots).'
        })

    def test_authentication_failure_fake_token_provided_on_post(self):
        response = self.client.post('/requires_authentication', headers={'Authorization': 'Bearer Fake token'})
        self.assert401(response)
        self.assert_json(response, {
            'message': 'Invalid JWT Token (header, body and signature must be separated by dots).'
        })

    def test_authentication_failure_fake_token_provided_on_put(self):
        response = self.client.put('/requires_authentication', headers={'Authorization': 'Bearer Fake token'})
        self.assert401(response)
        self.assert_json(response, {
            'message': 'Invalid JWT Token (header, body and signature must be separated by dots).'
        })

    def test_authentication_failure_fake_token_provided_on_delete(self):
        response = self.client.delete('/requires_authentication', headers={'Authorization': 'Bearer Fake token'})
        self.assert401(response)
        self.assert_json(response, {
            'message': 'Invalid JWT Token (header, body and signature must be separated by dots).'
        })

    def test_authentication_failure_invalid_key_identifier_in_token_on_get(self):
        response = self.client.get('/requires_authentication', headers={
            'Authorization': 'Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiIsIng1dCI6IlNTUWRoSTFjS3ZoUUVEU0p4RTJnR1lzNDBRMC'
                             'IsImtpZCI6IlNTUWRoSTFjS3ZoUUVEU0p4RTJnR1lzNDBRMCJ9.eyJhdWQiOiIyYmVmNzMzZC03NWJlLTQxNTktYj'
                             'I4MC02NzJlMDU0OTM4YzMiLCJpc3MiOiJodHRwczovL3N0cy53aW5kb3dzLm5ldC8yNDEzOWQxNC1jNjJjLTRjNDc'
                             'tOGJkZC1jZTcxZWExZDUwY2YvIiwiaWF0IjoxNTIwMjcwNTAxLCJuYmYiOjE1MjAyNzA1MDEsImV4cCI6MTUyMDI3'
                             'NDQwMSwiYWlvIjoiWTJOZ1lFaHlXMjYwVS9kR1RGeWNTMWNPVnczYnpqVXQ0Zk96TkNTekJYaWMyWTVOWFFNQSIsI'
                             'mFtciI6WyJwd2QiXSwiZmFtaWx5X25hbWUiOiJCb3Vub3VhciIsImdpdmVuX25hbWUiOiJDb2xpbiIsImlwYWRkci'
                             'I6IjE5NC4yOS45OC4xNDQiLCJuYW1lIjoiQm91bm91YXIgQ29saW4gKEVOR0lFIEVuZXJneSBNYW5hZ2VtZW50KSI'
                             'sIm5vbmNlIjoiW1x1MDAyNzczNjJDQUVBLTlDQTUtNEI0My05QkEzLTM0RDdDMzAzRUJBN1x1MDAyN10iLCJvaWQi'
                             'OiJkZTZiOGVjYS01ZTEzLTRhZTEtODcyMS1mZGNmNmI0YTljZGQiLCJvbnByZW1fc2lkIjoiUy0xLTUtMjEtMTQwO'
                             'TA4MjIzMy0xNDE3MDAxMzMzLTY4MjAwMzMzMC0zNzY5NTQiLCJzdWIiOiI2eEZSV1FBaElOZ0I4Vy10MnJRVUJzcE'
                             'lGc1VyUXQ0UUZ1V1VkSmRxWFdnIiwidGlkIjoiMjQxMzlkMTQtYzYyYy00YzQ3LThiZGQtY2U3MWVhMWQ1MGNmIiw'
                             'idW5pcXVlX25hbWUiOiJKUzUzOTFAZW5naWUuY29tIiwidXBuIjoiSlM1MzkxQGVuZ2llLmNvbSIsInV0aSI6InVm'
                             'M0x0X1Q5aWsyc0hGQ01oNklhQUEiLCJ2ZXIiOiIxLjAifQ.addwLSoO-2t1kXgljqnaU-P1hQGHQBiJMcNCLwELhB'
                             'ZT_vHvkZHFrmgfcTzED_AMdB9mTpvUm_Mk0d3F3RzLtyCeAApOPJaRAwccAc3PB1pKTwjFhdzIXtxib0_MQ6_F1fh'
                             'b8R8ZcLCbwhMtT8nXoeWJOvH9_71O_vkfOn6E-VwLo17jkvQJOa89KfctGNnHNMcPBBju0oIgp_UVal311SMUw_10'
                             'i4GZZkjR2I1m7EMg5jMwQgUatYWv2J5HoefAQQDat9jJeEnYNITxsJMN81FHTyuvMnN_ulFzOGtcvlBpmP6jVHfED'
                             'oJiqFM4NFh6r4IlOs2U2-jUb_bR5xi2zg'
        })
        self.assert401(response)
        self.assert_json_regex(
            response,
            "\{'message': \"SSQdhI1cKvhQEDSJxE2gGYs40Q0 is not a valid key identifier. Valid ones are .*\"\}"
        )

    def test_authentication_failure_invalid_key_identifier_in_token_on_post(self):
        response = self.client.post('/requires_authentication', headers={
            'Authorization': 'Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiIsIng1dCI6IlNTUWRoSTFjS3ZoUUVEU0p4RTJnR1lzNDBRMC'
                             'IsImtpZCI6IlNTUWRoSTFjS3ZoUUVEU0p4RTJnR1lzNDBRMCJ9.eyJhdWQiOiIyYmVmNzMzZC03NWJlLTQxNTktYj'
                             'I4MC02NzJlMDU0OTM4YzMiLCJpc3MiOiJodHRwczovL3N0cy53aW5kb3dzLm5ldC8yNDEzOWQxNC1jNjJjLTRjNDc'
                             'tOGJkZC1jZTcxZWExZDUwY2YvIiwiaWF0IjoxNTIwMjcwNTAxLCJuYmYiOjE1MjAyNzA1MDEsImV4cCI6MTUyMDI3'
                             'NDQwMSwiYWlvIjoiWTJOZ1lFaHlXMjYwVS9kR1RGeWNTMWNPVnczYnpqVXQ0Zk96TkNTekJYaWMyWTVOWFFNQSIsI'
                             'mFtciI6WyJwd2QiXSwiZmFtaWx5X25hbWUiOiJCb3Vub3VhciIsImdpdmVuX25hbWUiOiJDb2xpbiIsImlwYWRkci'
                             'I6IjE5NC4yOS45OC4xNDQiLCJuYW1lIjoiQm91bm91YXIgQ29saW4gKEVOR0lFIEVuZXJneSBNYW5hZ2VtZW50KSI'
                             'sIm5vbmNlIjoiW1x1MDAyNzczNjJDQUVBLTlDQTUtNEI0My05QkEzLTM0RDdDMzAzRUJBN1x1MDAyN10iLCJvaWQi'
                             'OiJkZTZiOGVjYS01ZTEzLTRhZTEtODcyMS1mZGNmNmI0YTljZGQiLCJvbnByZW1fc2lkIjoiUy0xLTUtMjEtMTQwO'
                             'TA4MjIzMy0xNDE3MDAxMzMzLTY4MjAwMzMzMC0zNzY5NTQiLCJzdWIiOiI2eEZSV1FBaElOZ0I4Vy10MnJRVUJzcE'
                             'lGc1VyUXQ0UUZ1V1VkSmRxWFdnIiwidGlkIjoiMjQxMzlkMTQtYzYyYy00YzQ3LThiZGQtY2U3MWVhMWQ1MGNmIiw'
                             'idW5pcXVlX25hbWUiOiJKUzUzOTFAZW5naWUuY29tIiwidXBuIjoiSlM1MzkxQGVuZ2llLmNvbSIsInV0aSI6InVm'
                             'M0x0X1Q5aWsyc0hGQ01oNklhQUEiLCJ2ZXIiOiIxLjAifQ.addwLSoO-2t1kXgljqnaU-P1hQGHQBiJMcNCLwELhB'
                             'ZT_vHvkZHFrmgfcTzED_AMdB9mTpvUm_Mk0d3F3RzLtyCeAApOPJaRAwccAc3PB1pKTwjFhdzIXtxib0_MQ6_F1fh'
                             'b8R8ZcLCbwhMtT8nXoeWJOvH9_71O_vkfOn6E-VwLo17jkvQJOa89KfctGNnHNMcPBBju0oIgp_UVal311SMUw_10'
                             'i4GZZkjR2I1m7EMg5jMwQgUatYWv2J5HoefAQQDat9jJeEnYNITxsJMN81FHTyuvMnN_ulFzOGtcvlBpmP6jVHfED'
                             'oJiqFM4NFh6r4IlOs2U2-jUb_bR5xi2zg'
        })
        self.assert401(response)
        self.assert_json_regex(
            response,
            "\{'message': \"SSQdhI1cKvhQEDSJxE2gGYs40Q0 is not a valid key identifier. Valid ones are .*\"\}"
        )

    def test_authentication_failure_invalid_key_identifier_in_token_on_put(self):
        response = self.client.put('/requires_authentication', headers={
            'Authorization': 'Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiIsIng1dCI6IlNTUWRoSTFjS3ZoUUVEU0p4RTJnR1lzNDBRMC'
                             'IsImtpZCI6IlNTUWRoSTFjS3ZoUUVEU0p4RTJnR1lzNDBRMCJ9.eyJhdWQiOiIyYmVmNzMzZC03NWJlLTQxNTktYj'
                             'I4MC02NzJlMDU0OTM4YzMiLCJpc3MiOiJodHRwczovL3N0cy53aW5kb3dzLm5ldC8yNDEzOWQxNC1jNjJjLTRjNDc'
                             'tOGJkZC1jZTcxZWExZDUwY2YvIiwiaWF0IjoxNTIwMjcwNTAxLCJuYmYiOjE1MjAyNzA1MDEsImV4cCI6MTUyMDI3'
                             'NDQwMSwiYWlvIjoiWTJOZ1lFaHlXMjYwVS9kR1RGeWNTMWNPVnczYnpqVXQ0Zk96TkNTekJYaWMyWTVOWFFNQSIsI'
                             'mFtciI6WyJwd2QiXSwiZmFtaWx5X25hbWUiOiJCb3Vub3VhciIsImdpdmVuX25hbWUiOiJDb2xpbiIsImlwYWRkci'
                             'I6IjE5NC4yOS45OC4xNDQiLCJuYW1lIjoiQm91bm91YXIgQ29saW4gKEVOR0lFIEVuZXJneSBNYW5hZ2VtZW50KSI'
                             'sIm5vbmNlIjoiW1x1MDAyNzczNjJDQUVBLTlDQTUtNEI0My05QkEzLTM0RDdDMzAzRUJBN1x1MDAyN10iLCJvaWQi'
                             'OiJkZTZiOGVjYS01ZTEzLTRhZTEtODcyMS1mZGNmNmI0YTljZGQiLCJvbnByZW1fc2lkIjoiUy0xLTUtMjEtMTQwO'
                             'TA4MjIzMy0xNDE3MDAxMzMzLTY4MjAwMzMzMC0zNzY5NTQiLCJzdWIiOiI2eEZSV1FBaElOZ0I4Vy10MnJRVUJzcE'
                             'lGc1VyUXQ0UUZ1V1VkSmRxWFdnIiwidGlkIjoiMjQxMzlkMTQtYzYyYy00YzQ3LThiZGQtY2U3MWVhMWQ1MGNmIiw'
                             'idW5pcXVlX25hbWUiOiJKUzUzOTFAZW5naWUuY29tIiwidXBuIjoiSlM1MzkxQGVuZ2llLmNvbSIsInV0aSI6InVm'
                             'M0x0X1Q5aWsyc0hGQ01oNklhQUEiLCJ2ZXIiOiIxLjAifQ.addwLSoO-2t1kXgljqnaU-P1hQGHQBiJMcNCLwELhB'
                             'ZT_vHvkZHFrmgfcTzED_AMdB9mTpvUm_Mk0d3F3RzLtyCeAApOPJaRAwccAc3PB1pKTwjFhdzIXtxib0_MQ6_F1fh'
                             'b8R8ZcLCbwhMtT8nXoeWJOvH9_71O_vkfOn6E-VwLo17jkvQJOa89KfctGNnHNMcPBBju0oIgp_UVal311SMUw_10'
                             'i4GZZkjR2I1m7EMg5jMwQgUatYWv2J5HoefAQQDat9jJeEnYNITxsJMN81FHTyuvMnN_ulFzOGtcvlBpmP6jVHfED'
                             'oJiqFM4NFh6r4IlOs2U2-jUb_bR5xi2zg'
        })
        self.assert401(response)
        self.assert_json_regex(
            response,
            "\{'message': \"SSQdhI1cKvhQEDSJxE2gGYs40Q0 is not a valid key identifier. Valid ones are .*\"\}"
        )

    def test_authentication_failure_invalid_key_identifier_in_token_on_delete(self):
        response = self.client.delete('/requires_authentication', headers={
            'Authorization': 'Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiIsIng1dCI6IlNTUWRoSTFjS3ZoUUVEU0p4RTJnR1lzNDBRMC'
                             'IsImtpZCI6IlNTUWRoSTFjS3ZoUUVEU0p4RTJnR1lzNDBRMCJ9.eyJhdWQiOiIyYmVmNzMzZC03NWJlLTQxNTktYj'
                             'I4MC02NzJlMDU0OTM4YzMiLCJpc3MiOiJodHRwczovL3N0cy53aW5kb3dzLm5ldC8yNDEzOWQxNC1jNjJjLTRjNDc'
                             'tOGJkZC1jZTcxZWExZDUwY2YvIiwiaWF0IjoxNTIwMjcwNTAxLCJuYmYiOjE1MjAyNzA1MDEsImV4cCI6MTUyMDI3'
                             'NDQwMSwiYWlvIjoiWTJOZ1lFaHlXMjYwVS9kR1RGeWNTMWNPVnczYnpqVXQ0Zk96TkNTekJYaWMyWTVOWFFNQSIsI'
                             'mFtciI6WyJwd2QiXSwiZmFtaWx5X25hbWUiOiJCb3Vub3VhciIsImdpdmVuX25hbWUiOiJDb2xpbiIsImlwYWRkci'
                             'I6IjE5NC4yOS45OC4xNDQiLCJuYW1lIjoiQm91bm91YXIgQ29saW4gKEVOR0lFIEVuZXJneSBNYW5hZ2VtZW50KSI'
                             'sIm5vbmNlIjoiW1x1MDAyNzczNjJDQUVBLTlDQTUtNEI0My05QkEzLTM0RDdDMzAzRUJBN1x1MDAyN10iLCJvaWQi'
                             'OiJkZTZiOGVjYS01ZTEzLTRhZTEtODcyMS1mZGNmNmI0YTljZGQiLCJvbnByZW1fc2lkIjoiUy0xLTUtMjEtMTQwO'
                             'TA4MjIzMy0xNDE3MDAxMzMzLTY4MjAwMzMzMC0zNzY5NTQiLCJzdWIiOiI2eEZSV1FBaElOZ0I4Vy10MnJRVUJzcE'
                             'lGc1VyUXQ0UUZ1V1VkSmRxWFdnIiwidGlkIjoiMjQxMzlkMTQtYzYyYy00YzQ3LThiZGQtY2U3MWVhMWQ1MGNmIiw'
                             'idW5pcXVlX25hbWUiOiJKUzUzOTFAZW5naWUuY29tIiwidXBuIjoiSlM1MzkxQGVuZ2llLmNvbSIsInV0aSI6InVm'
                             'M0x0X1Q5aWsyc0hGQ01oNklhQUEiLCJ2ZXIiOiIxLjAifQ.addwLSoO-2t1kXgljqnaU-P1hQGHQBiJMcNCLwELhB'
                             'ZT_vHvkZHFrmgfcTzED_AMdB9mTpvUm_Mk0d3F3RzLtyCeAApOPJaRAwccAc3PB1pKTwjFhdzIXtxib0_MQ6_F1fh'
                             'b8R8ZcLCbwhMtT8nXoeWJOvH9_71O_vkfOn6E-VwLo17jkvQJOa89KfctGNnHNMcPBBju0oIgp_UVal311SMUw_10'
                             'i4GZZkjR2I1m7EMg5jMwQgUatYWv2J5HoefAQQDat9jJeEnYNITxsJMN81FHTyuvMnN_ulFzOGtcvlBpmP6jVHfED'
                             'oJiqFM4NFh6r4IlOs2U2-jUb_bR5xi2zg'
        })
        self.assert401(response)
        self.assert_json_regex(
            response,
            "\{'message': \"SSQdhI1cKvhQEDSJxE2gGYs40Q0 is not a valid key identifier. Valid ones are .*\"\}"
        )

    def test_log_get_request_details(self):
        response = self.client.get('/logging')
        self.assert200(response)
        self.assert_json(response, '')

    def test_log_delete_request_details(self):
        response = self.client.delete('/logging')
        self.assert200(response)
        self.assert_json(response, '')

    def test_log_post_request_details(self):
        response = self.client.post('/logging')
        self.assert200(response)
        self.assert_json(response, '')

    def test_log_put_request_details(self):
        response = self.client.put('/logging')
        self.assert200(response)
        self.assert_json(response, '')


class LoggingFilterTest(unittest.TestCase):

    def setUp(self):
        logger.info(f'-------------------------------')
        logger.info(f'Start of {self._testMethodName}')

    def tearDown(self):
        logger.info(f'End of {self._testMethodName}')
        logger.info(f'-------------------------------')

    def test_request_id_filter_without_flask(self):
        import collections, flask
        record = collections.namedtuple('TestRecord', [])
        flask._request_ctx_stack.push(None)
        logging_filter.RequestIdFilter().filter(record)
        self.assertEqual('', record.request_id)

    def test_request_id_filter_with_value_already_set_in_flask_globals(self):
        import collections, flask
        record = collections.namedtuple('TestRecord', [])
        flask._request_ctx_stack.push('SimulateFlaskContext')
        flask.g = collections.namedtuple('TestGlobals', 'request_id')(request_id='TestId')
        logging_filter.RequestIdFilter().filter(record)
        self.assertEqual('TestId', record.request_id)

    def test_request_id_filter_with_value_not_set_in_header(self):
        import collections, flask, uuid
        record = collections.namedtuple('TestRecord', [])
        flask._request_ctx_stack.push('SimulateFlaskContext')
        flask.g = collections.namedtuple('TestGlobals', [])
        TestRequest = collections.namedtuple('TestRequest', 'headers')
        flask.request = TestRequest(headers={})
        logging_filter.RequestIdFilter().filter(record)
        self.assertTrue(isinstance(record.request_id, uuid.UUID))

    def test_request_id_filter_with_value_set_in_header(self):
        import collections, flask
        record = collections.namedtuple('TestRecord', [])
        flask._request_ctx_stack.push('SimulateFlaskContext')
        flask.g = collections.namedtuple('TestGlobals', [])
        TestRequest = collections.namedtuple('TestRequest', 'headers')
        flask.request = TestRequest(headers={'X-Request-Id': 'PreviousId'})
        logging_filter.RequestIdFilter().filter(record)
        self.assertRegex(record.request_id, 'PreviousId,.*-.*-.*-.*-.*')

    def test_user_id_filter_without_flask(self):
        import collections, flask
        record = collections.namedtuple('TestRecord', [])
        flask._request_ctx_stack.push(None)
        logging_filter.UserIdFilter().filter(record)
        self.assertEqual('', record.user_id)

    def test_user_id_filter_with_value_already_set_in_flask_globals(self):
        import collections, flask
        record = collections.namedtuple('TestRecord', [])
        flask._request_ctx_stack.push('SimulateFlaskContext')
        flask.g = collections.namedtuple('TestGlobals', 'user_id')(user_id='TestId')
        logging_filter.UserIdFilter().filter(record)
        self.assertEqual('TestId', record.user_id)

    def test_user_id_filter_with_value_not_set_in_header(self):
        import collections, flask
        record = collections.namedtuple('TestRecord', [])
        flask._request_ctx_stack.push('SimulateFlaskContext')
        flask.g = collections.namedtuple('TestGlobals', [])
        logging_filter.UserIdFilter().filter(record)
        self.assertEqual('anonymous', record.user_id)


class WindowsTest(unittest.TestCase):

    def setUp(self):
        logger.info(f'-------------------------------')
        logger.info(f'Start of {self._testMethodName}')
        mock_now()

    def tearDown(self):
        revert_now()
        TestConnection.reset()
        logger.info(f'End of {self._testMethodName}')
        logger.info(f'-------------------------------')

    def test_successful_connection(self):
        self.assertIsNotNone(windows.connect('TestComputer', '127.0.0.1', 80, 'TestDomain', 'TestUser', 'TestPassword'))

    def test_connection_failure(self):
        TestConnection.should_connect = False
        with self.assertRaises(Exception) as cm:
            windows.connect('TestComputer', '127.0.0.1', 80, 'TestDomain', 'TestUser', 'TestPassword')
        self.assertEqual('Impossible to connect to TestComputer (127.0.0.1:80), '
                         'check connectivity or TestDomain\TestUser rights.', str(cm.exception))

    def test_pass_health_check(self):
        connection = windows.connect('TestComputer', '127.0.0.1', 80, 'TestDomain', 'TestUser', 'TestPassword')
        TestConnection.echo_responses[b''] = b''
        self.assertEqual(('pass', {
            'test:echo': {
                'componentType': 'TestComputer',
                'observedValue': '',
                'status': 'pass',
                'time': '2018-10-11T15:05:05.663979',
            }
        }), windows.health_details('test', connection))

    def test_fail_health_check(self):
        connection = windows.connect('TestComputer', '127.0.0.1', 80, 'TestDomain', 'TestUser', 'TestPassword')
        self.assertEqual(('fail', {
            'test:echo': {
                'componentType': 'TestComputer',
                'status': 'fail',
                'time': '2018-10-11T15:05:05.663979',
                'output': f'Mock for echo failure.{os.linesep}',
            }
        }), windows.health_details('test', connection))

    def test_file_retrieval(self):
        connection = windows.connect('TestComputer', '127.0.0.1', 80, 'TestDomain', 'TestUser', 'TestPassword')
        with tempfile.TemporaryDirectory() as temp_dir:
            TestConnection.files_to_retrieve[('TestShare', 'TestFilePath')] = 'Test Content'

            windows.get(connection, 'TestShare', 'TestFilePath', os.path.join(temp_dir, 'local_file'))
            with open(os.path.join(temp_dir, 'local_file')) as local_file:
                self.assertEqual(local_file.read(), 'Test Content')

    def test_file_move(self):
        connection = windows.connect('TestComputer', '127.0.0.1', 80, 'TestDomain', 'TestUser', 'TestPassword')
        with tempfile.TemporaryDirectory() as temp_dir:
            with open(os.path.join(temp_dir, 'local_file'), mode='w') as distant_file:
                distant_file.write('Test Content Move')

            windows.move(connection, 'TestShare', 'TestFilePath', os.path.join(temp_dir, 'local_file'))

            self.assertEqual(TestConnection.stored_files[('TestShare', 'TestFilePath')], 'Test Content Move')

    def test_file_rename(self):
        connection = windows.connect('TestComputer', '127.0.0.1', 80, 'TestDomain', 'TestUser', 'TestPassword')

        TestConnection.stored_files[('TestShare/', 'file_to_rename')] = 'Test Rename'

        windows.rename(connection, 'TestShare/', 'file_to_rename', 'file_new_name')

        self.assertNotIn(('TestShare/', 'file_to_rename'), TestConnection.stored_files)
        self.assertEqual(TestConnection.stored_files[('TestShare/', 'file_new_name')], 'Test Rename')

    def test_file_rename_file_does_not_exist(self):
        connection = windows.connect('TestComputer', '127.0.0.1', 80, 'TestDomain', 'TestUser', 'TestPassword')

        with self.assertRaises(FileNotFoundError) as cm:
            windows.rename(connection, 'TestShare\\', 'file_to_rename_2', 'file_new_name')

        self.assertEqual(str(cm.exception), r"\\TestComputer\TestShare\file_to_rename_2 doesn't exist")

    def test_get_file_desc_file_exists(self):
        connection = windows.connect('TestComputer', '127.0.0.1', 80, 'TestDomain', 'TestUser', 'TestPassword')

        TestConnection.stored_files[('TestShare/', 'file_to_find')] = 'Test Find'

        founded_file = windows.get_file_desc(connection, 'TestShare/', 'file_to_find')

        self.assertEqual(founded_file.filename, 'file_to_find')

    def test_get_file_desc_file_does_not_exist(self):
        connection = windows.connect('TestComputer', '127.0.0.1', 80, 'TestDomain', 'TestUser', 'TestPassword')

        TestConnection.stored_files[('TestShare/', 'file_to_find')] = 'Test Find'

        founded_file = windows.get_file_desc(connection, 'TestShare/', 'nonexistent_file_to_find')

        self.assertIsNone(founded_file)


class CreateNewApi(unittest.TestCase):
    def test_basic_api(self):
        app, api = flask_restplus_common.create_api(__file__, title='TestApi', description='Testing API', cors=False,
                                                    reverse_proxy=False)

        with app.test_client() as client:
            response = client.get('/swagger.json')
            JSONTestCase().assert_200(response)
            JSONTestCase().assert_json(response, {'swagger': '2.0', 'basePath': '/', 'paths': {},
                                                  'info': {'title': 'TestApi', 'version': '1.0.0',
                                                           'description': 'Testing API'},
                                                  'produces': ['application/json'], 'consumes': ['application/json'],
                                                  'tags': [], 'responses': {
                    'ParseError': {'description': "When a mask can't be parsed"},
                    'MaskError': {'description': 'When any error occurs on mask'}}})

    def test_cors_api(self):
        app, api = flask_restplus_common.create_api(__file__, title='TestApi', description='Testing API',
                                                    reverse_proxy=False)

        with app.test_client() as client:
            response = client.get('/swagger.json')
            JSONTestCase().assert_200(response)
            JSONTestCase().assert_json(response, {'swagger': '2.0', 'basePath': '/', 'paths': {},
                                                  'info': {'title': 'TestApi', 'version': '1.0.0',
                                                           'description': 'Testing API'},
                                                  'produces': ['application/json'], 'consumes': ['application/json'],
                                                  'tags': [], 'responses': {
                    'ParseError': {'description': "When a mask can't be parsed"},
                    'MaskError': {'description': 'When any error occurs on mask'}}})
            self.assertEqual(response.headers.get('Access-Control-Allow-Origin'), '*')

    def test_compress_api(self):
        app, api = flask_restplus_common.create_api(__file__, title='TestApi', description='Testing API', cors=False,
                                                    reverse_proxy=False,
                                                    compress_mimetypes=['application/json'])

        heavy_answer = {'test': 1000 * 'A'}

        @api.route('/test')
        class TestRoute(Resource):
            def get(self):
                return Response(response=json.dumps(heavy_answer), mimetype='application/json')

        with app.test_client() as client:
            response = client.get('/test', headers=[('Accept-Encoding', 'gzip')])
            JSONTestCase().assert_200(response)
            self.assertEqual(response.content_encoding, 'gzip')
            mock_response = Mock(data=gzip.decompress(response.data))
            JSONTestCase().assert_json(mock_response, heavy_answer)

    def test_reverse_proxy_api(self):
        app, api = flask_restplus_common.create_api(__file__, title='TestApi', description='Testing API', cors=False)

        with app.test_client() as client:
            response = client.get('/swagger.json', headers=[('X-Original-Request-Uri', '/behind_reverse_proxy')])
            JSONTestCase().assert_200(response)
            JSONTestCase().assert_json(response, {'swagger': '2.0', 'basePath': '/behind_reverse_proxy', 'paths': {},
                                                  'info': {'title': 'TestApi', 'version': '1.0.0',
                                                           'description': 'Testing API'},
                                                  'produces': ['application/json'], 'consumes': ['application/json'],
                                                  'tags': [], 'responses': {
                    'ParseError': {'description': "When a mask can't be parsed"},
                    'MaskError': {'description': 'When any error occurs on mask'}}})

    def test_extra_parameters_api(self):
        app, api = flask_restplus_common.create_api(__file__, title='TestApi', description='Testing API', cors=False,
                                                    reverse_proxy=False, license_url='engie.license.com',
                                                    license='engie')

        with app.test_client() as client:
            response = client.get('/swagger.json', headers=[('X-Original-Request-Uri', '/behind_reverse_proxy')])
            JSONTestCase().assert_200(response)
            JSONTestCase().assert_json(response, {'swagger': '2.0', 'basePath': '/', 'paths': {},
                                                  'info': {'title': 'TestApi', 'version': '1.0.0',
                                                           'description': 'Testing API',
                                                           'license': {'name': 'engie', 'url': 'engie.license.com'}},
                                                  'produces': ['application/json'], 'consumes': ['application/json'],
                                                  'tags': [], 'responses': {
                    'ParseError': {'description': "When a mask can't be parsed"},
                    'MaskError': {'description': 'When any error occurs on mask'}}})


class HealthTest(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        mock_now()

    @classmethod
    def tearDownClass(cls):
        revert_now()

    def setUp(self):
        logger.info(f'-------------------------------')
        logger.info(f'Start of {self._testMethodName}')

    def tearDown(self):
        logger.info(f'End of {self._testMethodName}')
        logger.info(f'-------------------------------')

    @responses.activate
    def test_exception_health_check(self):
        self.assertEqual(('fail', {
            'test:health': {
                'componentType': 'http://test/health',
                'output': 'Connection refused: GET http://test/health',
                'status': 'fail',
                'time': '2018-10-11T15:05:05.663979'
            }
        }), health.http_details('test', 'http://test/health'))

    @responses.activate
    def test_error_health_check(self):
        responses.add(
            url='http://test/health',
            method=responses.GET,
            status=500,
            json={
                'message': 'An error occurred',
            }
        )
        self.assertEqual(('fail', {
            'test:health': {
                'componentType': 'http://test/health',
                'output': '{"message": "An error occurred"}',
                'status': 'fail',
                'time': '2018-10-11T15:05:05.663979'
            }
        }), health.http_details('test', 'http://test/health'))

    @responses.activate
    def test_pass_status_health_check(self):
        responses.add(
            url='http://test/health',
            method=responses.GET,
            status=200,
            json={
                'status': 'pass',
                'version': '1',
                'releaseId': '1.2.3',
                'details': {'toto': 'tata'},
            }
        )
        self.assertEqual(('pass', {
            'test:health': {
                'componentType': 'http://test/health',
                'observedValue': {
                    'details': {'toto': 'tata'},
                    'releaseId': '1.2.3',
                    'status': 'pass',
                    'version': '1'
                },
                'status': 'pass',
                'time': '2018-10-11T15:05:05.663979'
            }
        }), health.http_details('test', 'http://test/health'))

    @responses.activate
    def test_pass_status_health_check_with_health_content_type(self):
        responses.add(
            url='http://test/health',
            method=responses.GET,
            status=200,
            body=json.dumps({
                'status': 'pass',
                'version': '1',
                'releaseId': '1.2.3',
                'details': {'toto': 'tata'},
            }),
            content_type='application/health+json',
        )
        self.assertEqual(('pass', {
            'test:health': {
                'componentType': 'http://test/health',
                'observedValue': {
                    'details': {'toto': 'tata'},
                    'releaseId': '1.2.3',
                    'status': 'pass',
                    'version': '1'
                },
                'status': 'pass',
                'time': '2018-10-11T15:05:05.663979'
            }
        }), health.http_details('test', 'http://test/health'))

    @responses.activate
    def test_pass_status_custom_health_check(self):
        responses.add(
            url='http://test/status',
            method=responses.GET,
            status=200,
            body='pong'
        )
        self.assertEqual(('pass', {
            'test:health': {
                'componentType': 'http://test/status',
                'observedValue': 'pong',
                'status': 'pass',
                'time': '2018-10-11T15:05:05.663979'
            }
        }), health.http_details('test', 'http://test/status', lambda resp: 'pass'))

    @responses.activate
    def test_pass_status_custom_health_check_with_default_extractor(self):
        responses.add(
            url='http://test/status',
            method=responses.GET,
            status=200,
            body='pong'
        )
        self.assertEqual(('pass', {
            'test:health': {
                'componentType': 'http://test/status',
                'observedValue': 'pong',
                'status': 'pass',
                'time': '2018-10-11T15:05:05.663979'
            }
        }), health.http_details('test', 'http://test/status'))

    @responses.activate
    def test_warn_status_health_check(self):
        responses.add(
            url='http://test/health',
            method=responses.GET,
            status=200,
            json={
                'status': 'warn',
                'version': '1',
                'releaseId': '1.2.3',
                'details': {'toto': 'tata'},
            }
        )
        self.assertEqual(('warn', {
            'test:health': {
                'componentType': 'http://test/health',
                'observedValue': {
                    'details': {'toto': 'tata'},
                    'releaseId': '1.2.3',
                    'status': 'warn',
                    'version': '1'
                },
                'status': 'warn',
                'time': '2018-10-11T15:05:05.663979'
            }
        }), health.http_details('test', 'http://test/health'))

    @responses.activate
    def test_pass_status_custom_health_check(self):
        responses.add(
            url='http://test/status',
            method=responses.GET,
            status=200,
            body='pong'
        )
        self.assertEqual(('warn', {
            'test:health': {
                'componentType': 'http://test/status',
                'observedValue': 'pong',
                'status': 'warn',
                'time': '2018-10-11T15:05:05.663979'
            }
        }), health.http_details('test', 'http://test/status', lambda resp: 'warn'))

    @responses.activate
    def test_fail_status_health_check(self):
        responses.add(
            url='http://test/health',
            method=responses.GET,
            status=200,
            json={
                'status': 'fail',
                'version': '1',
                'releaseId': '1.2.3',
                'details': {'toto': 'tata'},
            }
        )
        self.assertEqual(('fail', {
            'test:health': {
                'componentType': 'http://test/health',
                'observedValue': {
                    'details': {'toto': 'tata'},
                    'releaseId': '1.2.3',
                    'status': 'fail',
                    'version': '1'
                },
                'status': 'fail',
                'time': '2018-10-11T15:05:05.663979'
            }
        }), health.http_details('test', 'http://test/health'))

    @responses.activate
    def test_fail_status_custom_health_check(self):
        responses.add(
            url='http://test/status',
            method=responses.GET,
            status=200,
            body='pong'
        )
        self.assertEqual(('fail', {
            'test:health': {
                'componentType': 'http://test/status',
                'observedValue': 'pong',
                'status': 'fail',
                'time': '2018-10-11T15:05:05.663979'
            }
        }), health.http_details('test', 'http://test/status', lambda resp: 'fail'))

    @responses.activate
    def test_fail_status_when_server_is_down(self):
        self.assertEqual(('fail', {
            'test:health': {
                'componentType': 'http://test/status',
                'output': 'Connection refused: GET http://test/status',
                'status': 'fail',
                'time': '2018-10-11T15:05:05.663979'
            }
        }), health.http_details('test', 'http://test/status'))

    def test_status_aggregation_with_failure(self):
        self.assertEqual('fail', health.status('pass', 'fail', 'warn'))

    def test_status_aggregation_with_warning(self):
        self.assertEqual('warn', health.status('pass', 'warn', 'pass'))

    def test_status_aggregation_with_pass(self):
        self.assertEqual('pass', health.status('pass', 'pass', 'pass'))


if __name__ == '__main__':
    unittest.main()
