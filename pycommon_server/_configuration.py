import logging
import logging.config
import os
import os.path
import sys

import yaml

logger = logging.getLogger(__name__)


def load(server_file_path: str) -> dict:
    """
    Load logging and server YAML configurations according to SERVER_ENVIRONMENT environment variable.

    :param server_file_path: Path to the server.py file (or any other file located in the python module directory).
    :return: server configuration as a dictionary.
    """
    module_directory = os.path.abspath(os.path.dirname(server_file_path))
    configuration_folder = os.path.join(module_directory, "..", "configuration")
    load_logging_configuration(configuration_folder)
    return load_configuration(configuration_folder)


def load_logging_configuration(configuration_folder: str) -> str:
    """
    Load logging configuration according to SERVER_ENVIRONMENT environment variable.
    If file is not found, then logging will be performed as INFO into stdout.
    Return loaded configuration file path. None if not loaded.
    """
    file_path = os.path.join(configuration_folder, f"logging_{get_environment()}.yml")
    return _load_logging_configuration(file_path)


def get_environment():
    """Return current server environment."""
    return os.environ.get("SERVER_ENVIRONMENT", "default")


def _load_logging_configuration(file_path: str) -> str:
    """
    Load YAML logging configuration file_path.
    If file is not found, then logging will be performed as INFO into stdout.
    """
    if os.path.isfile(file_path):
        with open(file_path, "r") as config_file:
            logging.config.dictConfig(yaml.full_load(config_file))
        logger.info(f"Logging configuration file ({file_path}) loaded.")
        return file_path
    else:
        logging.basicConfig(
            format="%(asctime)s - %(levelname)s - %(process)d:%(thread)d - %(filename)s:%(lineno)d - %(message)s",
            handlers=[logging.StreamHandler(sys.stdout)],
            level=logging.INFO,
        )
        logger.warning(
            f"Logging configuration file ({file_path}) cannot be found. Using standard output."
        )


def load_configuration(configuration_folder: str) -> dict:
    """
    Load configuration according to SERVER_ENVIRONMENT environment variable.
    Return a dictionary (empty if file cannot be found).
    """
    file_path = os.path.join(
        configuration_folder, f"configuration_{get_environment()}.yml"
    )
    return _load_configuration(file_path)


def _load_configuration(file_path: str) -> dict:
    """
    Load YAML configuration file path.
    Return a dictionary (empty if file cannot be found).
    """
    if os.path.isfile(file_path):
        with open(file_path, "r") as config_file:
            conf = yaml.full_load(config_file)
            logger.info(f"Loading configuration from {file_path}.")
            return conf
    else:
        logger.warning(
            f"Configuration file {file_path} cannot be found. Considering as empty."
        )
        return {}
