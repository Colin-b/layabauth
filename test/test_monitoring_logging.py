import pytest
import flask
import flask_restplus

import pycommon_server._monitoring


@pytest.fixture
def app():
    application = flask.Flask(__name__)
    application.testing = True
    api = flask_restplus.Api(application)

    @api.route("/logging")
    class Logging(flask_restplus.Resource):
        @pycommon_server._monitoring._log_request_details
        def get(self):
            return ""

        @pycommon_server._monitoring._log_request_details
        def post(self):
            return ""

        @pycommon_server._monitoring._log_request_details
        def put(self):
            return ""

        @pycommon_server._monitoring._log_request_details
        def delete(self):
            return ""

    return application


def test_generated_swagger(client):
    response = client.get("/swagger.json")
    assert response.status_code == 200
    assert response.json == {
        "swagger": "2.0",
        "basePath": "/",
        "paths": {
            "/logging": {
                "delete": {
                    "responses": {"200": {"description": "Success"}},
                    "operationId": "delete_logging",
                    "tags": ["default"],
                },
                "get": {
                    "responses": {"200": {"description": "Success"}},
                    "operationId": "get_logging",
                    "tags": ["default"],
                },
                "post": {
                    "responses": {"200": {"description": "Success"}},
                    "operationId": "post_logging",
                    "tags": ["default"],
                },
                "put": {
                    "responses": {"200": {"description": "Success"}},
                    "operationId": "put_logging",
                    "tags": ["default"],
                },
            }
        },
        "info": {"title": "API", "version": "1.0"},
        "produces": ["application/json"],
        "consumes": ["application/json"],
        "tags": [{"name": "default", "description": "Default namespace"}],
        "responses": {
            "ParseError": {"description": "When a mask can't be parsed"},
            "MaskError": {"description": "When any error occurs on mask"},
        },
    }


def test_log_get_request_details(client):
    response = client.get("/logging")
    assert response.status_code == 200
    assert response.json == ""


def test_log_delete_request_details(client):
    response = client.delete("/logging")
    assert response.status_code == 200
    assert response.json == ""


def test_log_post_request_details(client):
    response = client.post("/logging")
    assert response.status_code == 200
    assert response.json == ""


def test_log_put_request_details(client):
    response = client.put("/logging")
    assert response.status_code == 200
    assert response.json == ""
