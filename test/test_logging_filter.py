import collections
import re

import pytest
import flask

from pycommon_server import logging_filter


@pytest.fixture
def app():
    application = flask.Flask(__name__)
    application.testing = True

    @application.route("/request_id")
    def get_request_id():
        record = collections.namedtuple("TestRecord", [])
        logging_filter.RequestIdFilter().filter(record)
        return str(record.request_id)

    return application


def test_request_id_filter_with_value_not_set_in_header(client):
    response = client.get("/request_id")
    assert re.match(".*-.*-.*-.*-.*", response.get_data(as_text=True))


def test_request_id_filter_with_value_set_in_header(client):
    response = client.get(
        "/request_id", headers={"X-Request-Id": "ded1c926-d8bd-4886-96f1-b84b1f72b5d2"}
    )
    assert re.match(
        "ded1c926-d8bd-4886-96f1-b84b1f72b5d2,.*-.*-.*-.*-.*",
        response.get_data(as_text=True),
    )


def test_request_id_filter_with_value_already_set_in_flask_globals(client):
    response = client.get("/request_id")
    previous_id = response.get_data(as_text=True)
    response = client.get("/request_id")
    assert response.get_data(as_text=True) == previous_id


def test_request_id_filter_without_flask():
    record = collections.namedtuple("TestRecord", [])
    logging_filter.RequestIdFilter().filter(record)
    assert "" == record.request_id
