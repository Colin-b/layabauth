import pytest
from flask import Flask
from flask_restplus import Api

from pycommon_server import monitoring


@pytest.fixture
def app():
    application = Flask(__name__)
    application.testing = True
    api = Api(application, version="3.2.1")

    def throw_exception():
        raise Exception("This is the error message.")

    monitoring.add_monitoring_namespace(api, throw_exception)

    return application


def test_health_check_response_on_exception(client):
    response = client.get("/health")
    assert response.status_code == 400
    assert response.json == {
        "details": {},
        "output": "This is the error message.",
        "releaseId": "3.2.1",
        "status": "fail",
        "version": "3",
    }
