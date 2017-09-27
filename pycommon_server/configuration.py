import logging
import logging.config
import os.path
import os
import sys
import yaml


logger = logging.getLogger(__name__)


def load_logging_configuration(configuration_folder):
    """
    Load logging configuration according to ENVIRONMENT environment variable.
    If file is not found, then logging will be performed as INFO into stdout.
    """
    environment = os.environ.get('ENVIRONMENT', 'default')
    file_path = os.path.join(configuration_folder, f'logging_{environment}.yml')
    _load_logging_configuration(file_path)


def _load_logging_configuration(file_path):
    """
    Load YAML logging configuration file_path.
    If file is not found, then logging will be performed as INFO into stdout.
    """
    if os.path.isfile(file_path):
        with open(file_path, 'r') as config_file:
            logging.config.dictConfig(yaml.load(config_file))
        logger.info(f'Logging configuration file ({file_path}) loaded.')
    else:
        logging.basicConfig(
            format='%(asctime)s - %(levelname)s - %(process)d:%(thread)d - %(filename)s:%(lineno)d - %(message)s',
            handlers=[logging.StreamHandler(sys.stdout)],
            level=logging.INFO)
        logger.warning(f'Logging configuration file ({file_path}) cannot be found. Using standard output.')


def load_configuration(configuration_folder):
    """
    Load configuration according to ENVIRONMENT environment variable.
    Return a dictionary (empty if file cannot be found).
    """
    environment = os.environ.get('ENVIRONMENT', 'default')
    file_path = os.path.join(configuration_folder, f'configuration_{environment}.yml')
    return _load_configuration(file_path)


def _load_configuration(file_path):
    """
    Load YAML configuration file path.
    Return a dictionary (empty if file cannot be found).
    """
    if os.path.isfile(file_path):
        with open(file_path, 'r') as config_file:
            conf = yaml.load(config_file)
            logger.info(f'Loading configuration from {file_path}.')
            return conf
    else:
        logger.warning(f'Configuration file {file_path} cannot be found. Considering as empty.')
        return {}
