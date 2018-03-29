import os
import os.path
import tempfile
import unittest
import logging
from pycommon_test.flask_restplus_mock import TestAPI
from werkzeug.exceptions import Unauthorized

from pycommon_server.configuration import load_configuration, load_logging_configuration, load
from pycommon_server import flask_restplus_common, logging_filter

logger = logging.getLogger(__name__)


def _add_file(dir, file_name, *lines):
    with open(os.path.join(dir, file_name), 'w') as config_file:
        config_file.writelines('\n'.join(lines))


def _add_dir(dir, dir_name):
    dir_path = os.path.join(dir, dir_name)
    os.makedirs(os.path.join(dir, dir_name))
    return dir_path


class ConfigurationTest(unittest.TestCase):

    def setUp(self):
        logger.info(f'-------------------------------')
        logger.info(f'Start of {self._testMethodName}')
        os.environ.pop('ENVIRONMENT', None)

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


class FlaskRestPlusTest(unittest.TestCase):

    def setUp(self):
        logger.info(f'-------------------------------')
        logger.info(f'Start of {self._testMethodName}')

    def tearDown(self):
        logger.info(f'End of {self._testMethodName}')
        logger.info(f'-------------------------------')

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

    def test_authentication_failure_token_not_provided(self):
        @flask_restplus_common.RequiresAuthentication
        def get():
            return 'This should not be called.'
        # Avoid test failure due to decorator being called outside of a Flask request context
        import flask, collections
        TestRequest = collections.namedtuple('TestRequest', 'headers')
        flask.request = TestRequest(headers={})
        with self.assertRaises(Unauthorized) as cm:
            get()
        self.assertEqual('JWT Token is mandatory.', cm.exception.description)

    def test_authentication_failure_fake_token_provided(self):
        @flask_restplus_common.RequiresAuthentication
        def get():
            return 'This should not be called.'
        # Avoid test failure due to decorator being called outside of a Flask request context
        import flask, collections
        TestRequest = collections.namedtuple('TestRequest', 'headers')
        flask.request = TestRequest(headers={'Bearer': 'Fake token'})
        with self.assertRaises(Unauthorized) as cm:
            get()
        self.assertEqual('Invalid JWT Token (header, body and signature must be separated by dots).', cm.exception.description)

    def test_authentication_failure_expired_token_provided(self):
        @flask_restplus_common.RequiresAuthentication
        def get():
            return 'This should not be called.'
        # Avoid test failure due to decorator being called outside of a Flask request context
        import flask, collections
        TestRequest = collections.namedtuple('TestRequest', 'headers')
        flask.request = TestRequest(headers={'Bearer': '80a7f722779edd95cbc6c57f950881fa356222e086b379c0df8e5b847ddc34e9fddc78d3521f733f684c721b77f51a529cde7a7649c8f807a3f4358fd3a20d12'})
        with self.assertRaises(Unauthorized) as cm:
            get()

    def test_log_get_request_details(self):
        @flask_restplus_common.log_request_details
        def get():
            return 'Test get method is still called with decorator.'
        # Avoid test failure due to decorator being called outside of a Flask request context
        import flask, collections
        TestRequest = collections.namedtuple('TestRequest', 'data')
        flask.request = TestRequest(data=None)
        self.assertEqual('Test get method is still called with decorator.', get())

    def test_log_delete_request_details(self):
        @flask_restplus_common.log_request_details
        def delete():
            return 'Test get method is still called with decorator.'
        # Avoid test failure due to decorator being called outside of a Flask request context
        import flask, collections
        TestRequest = collections.namedtuple('TestRequest', 'data')
        flask.request = TestRequest(data=None)
        self.assertEqual('Test get method is still called with decorator.', delete())

    def test_log_post_request_details(self):
        @flask_restplus_common.log_request_details
        def post():
            return 'Test get method is still called with decorator.'
        # Avoid test failure due to decorator being called outside of a Flask request context
        import flask, collections
        TestRequest = collections.namedtuple('TestRequest', 'data')
        flask.request = TestRequest(data='{}')
        self.assertEqual('Test get method is still called with decorator.', post())

    def test_log_put_request_details(self):
        @flask_restplus_common.log_request_details
        def put():
            return 'Test get method is still called with decorator.'
        # Avoid test failure due to decorator being called outside of a Flask request context
        import flask, collections
        TestRequest = collections.namedtuple('TestRequest', 'data')
        flask.request = TestRequest(data='{}')
        self.assertEqual('Test get method is still called with decorator.', put())


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

    def test_request_id_filter_with_value_already_set_in_flask_flobals(self):
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

    def test_user_id_filter_with_value_already_set_in_flask_flobals(self):
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


if __name__ == '__main__':
    unittest.main()
