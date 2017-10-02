import os
import os.path
import tempfile
import unittest
import logging

from pycommon_server.configuration import load_configuration, load_logging_configuration
from pycommon_server import flask_restplus_common

logger = logging.getLogger(__name__)


def _add_file(dir, file_name, *lines):
    with open(os.path.join(dir, file_name), 'w') as config_file:
        config_file.writelines('\n'.join(lines))


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
        class TestApi:
            @classmethod
            def model(cls, name, fields):
                testable_fields = {key: value.default for key, value in fields.items()}
                return f'{name}: {testable_fields}'
        self.assertEqual("Successful: {'status': 'Successful'}",
                         flask_restplus_common.successful_model(TestApi))


if __name__ == '__main__':
    unittest.main()
