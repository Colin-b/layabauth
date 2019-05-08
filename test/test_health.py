import unittest
from unittest.mock import patch
import os

import redis
from pycommon_test import mock_now, revert_now

from pycommon_server.health import (
    redis_health_details
)


class RedisAndCeleryHealthTest(unittest.TestCase):
    def setUp(self):
        mock_now()

    def tearDown(self):
        revert_now()

    @patch.object(redis.Redis, "ping", return_value=1)
    @patch.object(redis.Redis, "keys", return_value=["kombu@/v1.2.3"])
    @patch.dict(os.environ, {"HOSTNAME": "my_host", "CONTAINER_NAME": "/v1.2.3"})
    def test_redis_health_details_ok(self, ping_mock, keys_mock):
        status, details = redis_health_details(
            {"celery": {"backend": "redis://test_url"}}
        )
        self.assertEqual(status, "pass")
        self.assertEqual(
            details,
            {
                "redis:ping": {
                    "componentType": "component",
                    "observedValue": "Namespace /v1.2.3_my_host can be found.",
                    "status": "pass",
                    "time": "2018-10-11T15:05:05.663979",
                }
            },
        )

    @patch.object(redis.Redis, "ping")
    def test_redis_health_details_cannot_connect_to_redis(self, ping_mock):
        ping_mock.side_effect = redis.exceptions.ConnectionError("Test message")

        status, details = redis_health_details(
            {"celery": {"backend": "redis://test_url"}}
        )
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

        status, details = redis_health_details(
            {"celery": {"backend": "redis://test_url"}}
        )
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
    @patch.dict(os.environ, {"HOSTNAME": "my_host", "CONTAINER_NAME": "/v1.2.3"})
    def test_redis_health_details_cannot_retrieve_keys_as_list(
        self, ping_mock, keys_mock
    ):
        status, details = redis_health_details(
            {"celery": {"backend": "redis://test_url"}}
        )
        self.assertEqual(status, "fail")
        self.assertEqual(
            details,
            {
                "redis:ping": {
                    "componentType": "component",
                    "status": "fail",
                    "time": "2018-10-11T15:05:05.663979",
                    "output": "Namespace /v1.2.3_my_host cannot be found in b'Those "
                    "are bytes'",
                }
            },
        )

    @patch.object(redis.Redis, "ping", return_value=1)
    @patch.object(redis.Redis, "keys", return_value=[b"kombu@/v1.2.3"])
    @patch.dict(os.environ, {"HOSTNAME": "my_host", "CONTAINER_NAME": "/v1.2.3"})
    def test_redis_health_details_retrieve_keys_as_bytes_list(
        self, ping_mock, keys_mock
    ):
        status, details = redis_health_details(
            {"celery": {"backend": "redis://test_url"}}
        )
        self.assertEqual(status, "pass")
        self.assertEqual(
            details,
            {
                "redis:ping": {
                    "componentType": "component",
                    "status": "pass",
                    "time": "2018-10-11T15:05:05.663979",
                    "observedValue": "Namespace /v1.2.3_my_host can be found.",
                }
            },
        )

    @patch.object(redis.Redis, "ping", return_value=1)
    @patch.object(redis.Redis, "keys", return_value=[])
    @patch.dict(os.environ, {"HOSTNAME": "my_host", "CONTAINER_NAME": "/v1.2.3"})
    def test_redis_health_details_missing_namespace(self, ping_mock, keys_mock):
        status, details = redis_health_details(
            {"celery": {"backend": "redis://test_url"}}
        )
        self.assertEqual(status, "fail")
        self.assertEqual(
            details,
            {
                "redis:ping": {
                    "componentType": "component",
                    "status": "fail",
                    "time": "2018-10-11T15:05:05.663979",
                    "output": "Namespace /v1.2.3_my_host cannot be found in []",
                }
            },
        )
