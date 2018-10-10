import os
import os.path
import tempfile
import unittest
import logging
from pycommon_test.flask_restplus_mock import TestAPI
from pycommon_test.samba_mock import TestConnection
from pycommon_test.service_tester import JSONTestCase
from flask import Flask
from flask_restplus import Resource, Api

from pycommon_server.configuration import load_configuration, load_logging_configuration, load
from pycommon_server import flask_restplus_common, logging_filter, windows

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
        os.environ.pop('ENVIRONMENT', None)
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

    def test_environment_configuration_loaded(self):
        os.environ['ENVIRONMENT'] = 'test'
        with tempfile.TemporaryDirectory() as tmp_dir:
            _add_file(tmp_dir, 'configuration_test.yml', 'section_test:', '  key: value')
            self.assertEqual(
                {
                    'section_test': {
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

    def test_environment_logging_configuration_loaded(self):
        os.environ['ENVIRONMENT'] = 'test'
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

    def test_all_environment_configurations_loaded(self):
        os.environ['ENVIRONMENT'] = 'test'
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


class FlaskRestPlusTest(JSONTestCase):
    def create_app(self):
        app = Flask(__name__)
        app.config['TESTING'] = True
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

        return app

    def test_successful_return(self):
        self.assertEqual(({'status': 'Successful'}, 200), flask_restplus_common.successful_return)

    def test_successful_deletion_return(self):
        self.assertEqual(('', 204), flask_restplus_common.successful_deletion_return)

    def test_successful_deletion_response(self):
        self.assertEqual((204, 'Sample deleted'), flask_restplus_common.successful_deletion_response)

    def test_successful_model(self):
        model = flask_restplus_common.successful_model(TestAPI)
        self.assertEqual('Successful', model.name)
        self.assertEqual({'status': 'Successful'}, model.fields_default)

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

    def tearDown(self):
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

        self.assertEqual(str(cm.exception),  r"\\TestComputer\TestShare\file_to_rename_2 doesn't exist")

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


if __name__ == '__main__':
    unittest.main()
