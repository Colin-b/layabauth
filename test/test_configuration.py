import os
import os.path
import tempfile

import pytest

import pycommon_server


def _add_file(folder: str, file_name: str, *lines) -> None:
    with open(os.path.join(folder, file_name), "w") as config_file:
        config_file.writelines("\n".join(lines))


def _add_dir(parent_folder: str, folder: str) -> str:
    folder_path = os.path.join(parent_folder, folder)
    os.makedirs(os.path.join(parent_folder, folder))
    return folder_path


@pytest.fixture
def remove_server_environment():
    yield 1
    os.environ.pop("SERVER_ENVIRONMENT", None)


def test_empty_configuration_if_file_not_found():
    with tempfile.TemporaryDirectory() as tmp_dir:
        assert {} == pycommon_server.load_configuration(tmp_dir)


def test_default_configuration_loaded_if_no_environment_specified():
    with tempfile.TemporaryDirectory() as tmp_dir:
        _add_file(
            tmp_dir, "configuration_default.yml", "section_default:", "  key: value"
        )
        assert {
            "section_default": {"key": "value"}
        } == pycommon_server.load_configuration(tmp_dir)


def test_environment_is_default_if_no_environment_specified():
    assert "default" == pycommon_server.get_environment()


def test_environment_is_server_environment(remove_server_environment):
    os.environ["SERVER_ENVIRONMENT"] = "test"
    assert "test" == pycommon_server.get_environment()


def test_server_environment_configuration_loaded(remove_server_environment):
    os.environ["SERVER_ENVIRONMENT"] = "test"
    with tempfile.TemporaryDirectory() as tmp_dir:
        _add_file(tmp_dir, "configuration_test.yml", "section_test:", "  key: value")
        assert {"section_test": {"key": "value"}} == pycommon_server.load_configuration(
            tmp_dir
        )


def test_hardcoded_default_logging_configuration_if_file_not_found():
    with tempfile.TemporaryDirectory() as tmp_dir:
        assert not pycommon_server.load_logging_configuration(tmp_dir)


def test_default_logging_configuration_loaded_if_no_environment_specified():
    with tempfile.TemporaryDirectory() as tmp_dir:
        _add_file(
            tmp_dir,
            "logging_default.yml",
            "version: 1",
            "formatters:",
            "  clean:",
            "    format: '%(message)s'",
            "handlers:",
            "  standard_output:",
            "    class: logging.StreamHandler",
            "    formatter: clean",
            "    stream: ext://sys.stdout",
            "root:",
            "  level: INFO",
            "  handlers: [standard_output]",
        )
        assert os.path.join(
            tmp_dir, "logging_default.yml"
        ) == pycommon_server.load_logging_configuration(tmp_dir)


def test_server_environment_logging_configuration_loaded(remove_server_environment):
    os.environ["SERVER_ENVIRONMENT"] = "test"
    with tempfile.TemporaryDirectory() as tmp_dir:
        _add_file(
            tmp_dir,
            "logging_test.yml",
            "version: 1",
            "formatters:",
            "  clean:",
            "    format: '%(message)s'",
            "handlers:",
            "  standard_output:",
            "    class: logging.StreamHandler",
            "    formatter: clean",
            "    stream: ext://sys.stdout",
            "root:",
            "  level: INFO",
            "  handlers: [standard_output]",
        )
        assert os.path.join(
            tmp_dir, "logging_test.yml"
        ) == pycommon_server.load_logging_configuration(tmp_dir)


def test_all_default_environment_configurations_loaded():
    with tempfile.TemporaryDirectory() as tmp_dir:
        configuration_folder = _add_dir(tmp_dir, "configuration")
        server_folder = _add_dir(tmp_dir, "my_server")
        _add_file(
            configuration_folder,
            "configuration_default.yml",
            "section_test:",
            "  key: value",
        )
        _add_file(
            configuration_folder,
            "logging_default.yml",
            "version: 1",
            "formatters:",
            "  clean:",
            "    format: '%(message)s'",
            "handlers:",
            "  standard_output:",
            "    class: logging.StreamHandler",
            "    formatter: clean",
            "    stream: ext://sys.stdout",
            "root:",
            "  level: INFO",
            "  handlers: [standard_output]",
        )
        assert {"section_test": {"key": "value"}} == pycommon_server.load(
            os.path.join(server_folder, "server.py")
        )


def test_all_server_environment_configurations_loaded(remove_server_environment):
    os.environ["SERVER_ENVIRONMENT"] = "test"
    with tempfile.TemporaryDirectory() as tmp_dir:
        configuration_folder = _add_dir(tmp_dir, "configuration")
        server_folder = _add_dir(tmp_dir, "my_server")
        _add_file(
            configuration_folder,
            "configuration_test.yml",
            "section_test:",
            "  key: value",
        )
        _add_file(
            configuration_folder,
            "logging_test.yml",
            "version: 1",
            "formatters:",
            "  clean:",
            "    format: '%(message)s'",
            "handlers:",
            "  standard_output:",
            "    class: logging.StreamHandler",
            "    formatter: clean",
            "    stream: ext://sys.stdout",
            "root:",
            "  level: INFO",
            "  handlers: [standard_output]",
        )
        assert {"section_test": {"key": "value"}} == pycommon_server.load(
            os.path.join(server_folder, "server.py")
        )
