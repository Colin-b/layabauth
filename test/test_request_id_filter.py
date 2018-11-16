import unittest
from collections import namedtuple

from pycommon_server import logging_filter


class RequestIdFilterTest(unittest.TestCase):

    def setUp(self):
        logging_filter.current_task = None

    def test_celery_is_none(self):
        req_filter = logging_filter.RequestIdFilter()
        dummy_record = namedtuple('Record', 'request_id')
        req_filter.filter(dummy_record)
        self.assertEqual('', dummy_record.request_id)

    def test_celery_is_not_none_but_request_is_none(self):
        logging_filter.current_task = namedtuple('DummyCelery', 'request')
        req_filter = logging_filter.RequestIdFilter()
        dummy_record = namedtuple('Record', 'request_id')
        req_filter.filter(dummy_record)
        self.assertEqual('', dummy_record.request_id)

    def test_request_not_none_but_id_is_none(self):
        logging_filter.current_task = namedtuple('DummyCelery', 'request')
        logging_filter.current_task.request = namedtuple('DummyCeleryRequest', 'aa')
        req_filter = logging_filter.RequestIdFilter()
        dummy_record = namedtuple('Record', 'request_id')
        req_filter.filter(dummy_record)
        self.assertEqual('', dummy_record.request_id)

    def test_request_none_is_none(self):
        logging_filter.current_task = namedtuple('DummyCelery', 'request')
        logging_filter.current_task.request = namedtuple('DummyCeleryRequest', 'id')
        logging_filter.current_task.request.id = 'bite my shiny metal ass'
        req_filter = logging_filter.RequestIdFilter()
        dummy_record = namedtuple('Record', 'request_id')
        req_filter.filter(dummy_record)
        self.assertEqual('bite my shiny metal ass', dummy_record.request_id)


if __name__ == '__main__':
    unittest.main()
