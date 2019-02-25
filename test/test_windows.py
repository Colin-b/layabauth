import logging
import os
import os.path
import tempfile
import unittest

from pycommon_test import mock_now, revert_now
from pycommon_test.samba_mock import TestConnection

from pycommon_server import windows

windows.SMBConnection = TestConnection

logger = logging.getLogger(__name__)


class WindowsTest(unittest.TestCase):
    def setUp(self):
        logger.info(f"-------------------------------")
        logger.info(f"Start of {self._testMethodName}")
        mock_now()

    def tearDown(self):
        revert_now()
        TestConnection.reset()
        logger.info(f"End of {self._testMethodName}")
        logger.info(f"-------------------------------")

    def test_successful_connection(self):
        self.assertIsNotNone(
            windows.connect(
                "TestComputer",
                "127.0.0.1",
                80,
                "TestDomain",
                "TestUser",
                "TestPassword",
            )
        )

    def test_connection_failure(self):
        TestConnection.should_connect = False
        with self.assertRaises(Exception) as cm:
            windows.connect(
                "TestComputer",
                "127.0.0.1",
                80,
                "TestDomain",
                "TestUser",
                "TestPassword",
            )
        self.assertEqual(
            "Impossible to connect to TestComputer (127.0.0.1:80), "
            "check connectivity or TestDomain\TestUser rights.",
            str(cm.exception),
        )

    def test_pass_health_check(self):
        connection = windows.connect(
            "TestComputer", "127.0.0.1", 80, "TestDomain", "TestUser", "TestPassword"
        )
        TestConnection.echo_responses[b""] = b""
        self.assertEqual(
            (
                "pass",
                {
                    "test:echo": {
                        "componentType": "TestComputer",
                        "observedValue": "",
                        "status": "pass",
                        "time": "2018-10-11T15:05:05.663979",
                    }
                },
            ),
            windows.health_details("test", connection),
        )

    def test_fail_health_check(self):
        connection = windows.connect(
            "TestComputer", "127.0.0.1", 80, "TestDomain", "TestUser", "TestPassword"
        )
        self.assertEqual(
            (
                "fail",
                {
                    "test:echo": {
                        "componentType": "TestComputer",
                        "status": "fail",
                        "time": "2018-10-11T15:05:05.663979",
                        "output": f"Mock for echo failure.{os.linesep}",
                    }
                },
            ),
            windows.health_details("test", connection),
        )

    def test_file_retrieval(self):
        connection = windows.connect(
            "TestComputer", "127.0.0.1", 80, "TestDomain", "TestUser", "TestPassword"
        )
        with tempfile.TemporaryDirectory() as temp_dir:
            TestConnection.files_to_retrieve[
                ("TestShare", "TestFilePath")
            ] = "Test Content"

            windows.get(
                connection,
                "TestShare",
                "TestFilePath",
                os.path.join(temp_dir, "local_file"),
            )
            with open(os.path.join(temp_dir, "local_file")) as local_file:
                self.assertEqual(local_file.read(), "Test Content")

    def test_file_move(self):
        connection = windows.connect(
            "TestComputer", "127.0.0.1", 80, "TestDomain", "TestUser", "TestPassword"
        )
        with tempfile.TemporaryDirectory() as temp_dir:
            with open(os.path.join(temp_dir, "local_file"), mode="w") as distant_file:
                distant_file.write("Test Content Move")

            windows.move(
                connection,
                "TestShare",
                "TestFilePath",
                os.path.join(temp_dir, "local_file"),
            )

            self.assertEqual(
                TestConnection.stored_files[("TestShare", "TestFilePath")],
                "Test Content Move",
            )

    def test_file_rename(self):
        connection = windows.connect(
            "TestComputer", "127.0.0.1", 80, "TestDomain", "TestUser", "TestPassword"
        )

        TestConnection.stored_files[("TestShare/", "file_to_rename")] = "Test Rename"

        windows.rename(connection, "TestShare/", "file_to_rename", "file_new_name")

        self.assertNotIn(("TestShare/", "file_to_rename"), TestConnection.stored_files)
        self.assertEqual(
            TestConnection.stored_files[("TestShare/", "file_new_name")], "Test Rename"
        )

    def test_file_rename_file_does_not_exist(self):
        connection = windows.connect(
            "TestComputer", "127.0.0.1", 80, "TestDomain", "TestUser", "TestPassword"
        )

        with self.assertRaises(FileNotFoundError) as cm:
            windows.rename(
                connection, "TestShare\\", "file_to_rename_2", "file_new_name"
            )

        self.assertEqual(
            str(cm.exception),
            r"\\TestComputer\TestShare\file_to_rename_2 doesn't exist",
        )

    def test_get_file_desc_file_exists(self):
        connection = windows.connect(
            "TestComputer", "127.0.0.1", 80, "TestDomain", "TestUser", "TestPassword"
        )

        TestConnection.stored_files[("TestShare/", "file_to_find")] = "Test Find"

        founded_file = windows.get_file_desc(connection, "TestShare/", "file_to_find")

        self.assertEqual(founded_file.filename, "file_to_find")

    def test_get_file_desc_file_does_not_exist(self):
        connection = windows.connect(
            "TestComputer", "127.0.0.1", 80, "TestDomain", "TestUser", "TestPassword"
        )

        TestConnection.stored_files[("TestShare/", "file_to_find")] = "Test Find"

        founded_file = windows.get_file_desc(
            connection, "TestShare/", "nonexistent_file_to_find"
        )

        self.assertIsNone(founded_file)


if __name__ == "__main__":
    unittest.main()
