import datetime
import json

import pytest
import pandas
from flask import Flask

from pycommon_server.pandas_responses import dataframe_as_json_response


@pytest.fixture
def app():
    application = Flask(__name__)
    application.testing = True
    return application


def test_dataframe_200(client):
    response = dataframe_as_json_response(
        pandas.DataFrame.from_dict(
            [
                {"key1": "row11", "key2": "row12"},
                {"key1": "row21", "key2": datetime.datetime(2018, 10, 11, 15, 0, 0)},
            ]
        )
    )
    assert json.loads(response.data) == [
        {"key1": "row11", "key2": "row12"},
        {"key1": "row21", "key2": "2018-10-11T15:00:00.000Z"},
    ]
    assert "application/json" == response.headers.get("Content-type")
    assert response.status_code == 200
