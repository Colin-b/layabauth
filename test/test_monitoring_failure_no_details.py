import pytest
from flask import Flask
from flask_restplus import Api

from pycommon_server import monitoring


@pytest.fixture
def app():
    application = Flask(__name__)
    application.testing = True
    api = Api(application, version="3.2.1")

    def failure_details():
        return "fail", None

    monitoring.add_monitoring_namespace(api, failure_details)

    return application


def test_health_check_response_on_exception(client):
    response = client.get("/health")
    assert response.status_code == 400
    assert response.json == {
        "details": None,
        "releaseId": "3.2.1",
        "status": "fail",
        "version": "3",
    }
