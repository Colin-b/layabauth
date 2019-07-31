import pytest
from flask import Flask
from flask_restplus import Api

from pycommon_server import monitoring


@pytest.fixture
def app():
    application = Flask(__name__)
    application.testing = True
    api = Api(application, version="3.2.1")

    def pass_details():
        return "pass", {"toto2": {"status": "pass"}}

    monitoring.add_monitoring_namespace(api, pass_details)
    return application


def test_changelog_not_found(client):
    response = client.get("/changelog")
    assert response.status_code == 500
    assert (
        response.get_data(as_text=True)
        == "No changelog can be found. Please contact support."
    )
