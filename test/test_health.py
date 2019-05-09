import unittest
from unittest.mock import patch

import redis
from pycommon_test import mock_now, revert_now

from pycommon_server.health import redis_details


class RedisHealthTest(unittest.TestCase):
    def setUp(self):
        mock_now()

    def tearDown(self):
        revert_now()

    @patch.object(redis.Redis, "ping", return_value=1)
    @patch.object(redis.Redis, "keys", return_value=["local"])
    def test_redis_health_details_ok(self, ping_mock, keys_mock):
        status, details = redis_details("redis://test_url", "local_my_host")
        self.assertEqual(status, "pass")
        self.assertEqual(
            details,
            {
                "redis:ping": {
                    "componentType": "component",
                    "observedValue": "local_my_host can be found.",
                    "status": "pass",
                    "time": "2018-10-11T15:05:05.663979",
                }
            },
        )

    @patch.object(redis.Redis, "ping")
    def test_redis_health_details_cannot_connect_to_redis(self, ping_mock):
        ping_mock.side_effect = redis.exceptions.ConnectionError("Test message")

        status, details = redis_details("redis://test_url", "")
        self.assertEqual(status, "fail")
        self.assertEqual(
            details,
            {
                "redis:ping": {
                    "componentType": "component",
                    "status": "fail",
                    "time": "2018-10-11T15:05:05.663979",
                    "output": "Test message",
                }
            },
        )

    @patch.object(redis.Redis, "from_url")
    def test_redis_health_details_cannot_retrieve_url(self, from_url_mock):
        from_url_mock.side_effect = redis.exceptions.ConnectionError("Test message")

        status, details = redis_details("redis://test_url", "")
        self.assertEqual(status, "fail")
        self.assertEqual(
            details,
            {
                "redis:ping": {
                    "componentType": "component",
                    "status": "fail",
                    "time": "2018-10-11T15:05:05.663979",
                    "output": "Test message",
                }
            },
        )

    @patch.object(redis.Redis, "ping", return_value=1)
    @patch.object(redis.Redis, "keys", return_value=b"Those are bytes")
    def test_redis_health_details_cannot_retrieve_keys_as_list(
        self, ping_mock, keys_mock
    ):
        status, details = redis_details("redis://test_url", "local_my_host")
        self.assertEqual(status, "fail")
        self.assertEqual(
            details,
            {
                "redis:ping": {
                    "componentType": "component",
                    "status": "fail",
                    "time": "2018-10-11T15:05:05.663979",
                    "output": "local_my_host cannot be found in b'Those " "are bytes'",
                }
            },
        )

    @patch.object(redis.Redis, "ping", return_value=1)
    @patch.object(redis.Redis, "keys", return_value=[b"local"])
    def test_redis_health_details_retrieve_keys_as_bytes_list(
        self, ping_mock, keys_mock
    ):
        status, details = redis_details("redis://test_url", "local_my_host")
        self.assertEqual(status, "pass")
        self.assertEqual(
            details,
            {
                "redis:ping": {
                    "componentType": "component",
                    "status": "pass",
                    "time": "2018-10-11T15:05:05.663979",
                    "observedValue": "local_my_host can be found.",
                }
            },
        )

    @patch.object(redis.Redis, "ping", return_value=1)
    @patch.object(redis.Redis, "keys", return_value=[])
    def test_redis_health_details_missing_key(self, ping_mock, keys_mock):
        status, details = redis_details("redis://test_url", "local_my_host")
        self.assertEqual(status, "fail")
        self.assertEqual(
            details,
            {
                "redis:ping": {
                    "componentType": "component",
                    "status": "fail",
                    "time": "2018-10-11T15:05:05.663979",
                    "output": "local_my_host cannot be found in []",
                }
            },
        )
