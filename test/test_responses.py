import json

import pytest
import flask
import flask_restplus

from pycommon_server import responses


@pytest.fixture
def app():
    application = flask.Flask(__name__)
    application.testing = True
    api = flask_restplus.Api(application)

    @api.route("/standard_responses")
    class StandardResponses(flask_restplus.Resource):
        @api.doc(**responses.created_response_doc(api))
        def post(self):
            return responses.created_response("/standard_responses?id=42")

        @api.doc(**responses.updated_response_doc(api))
        def put(self):
            return responses.updated_response("/standard_responses?id=43")

        @api.response(*responses.deleted_response_doc)
        def delete(self):
            return responses.deleted_response

    return application


def test_standard_post_response_without_reverse_proxy(client):
    response = client.post(
        "/standard_responses", data=json.dumps({}), content_type="application/json"
    )
    assert response.status_code == 201
    assert response.json == {"status": "Successful"}
    assert response.headers["location"] == "http://localhost/standard_responses?id=42"


def test_standard_post_response_with_reverse_proxy(client):
    response = client.post(
        "/standard_responses",
        data=json.dumps({}),
        content_type="application/json",
        headers={
            "X-Original-Request-Uri": "/reverse/standard_responses",
            "Host": "localhost",
        },
    )
    assert response.status_code == 201
    assert response.json == {"status": "Successful"}
    assert (
        response.headers["location"]
        == "http://localhost/reverse/standard_responses?id=42"
    )


def test_standard_put_response_without_reverse_proxy(client):
    response = client.put(
        "/standard_responses", data=json.dumps({}), content_type="application/json"
    )
    assert response.status_code == 201
    assert response.json == {"status": "Successful"}
    assert response.headers["location"] == "http://localhost/standard_responses?id=43"


def test_standard_put_response_with_reverse_proxy(client):
    response = client.put(
        "/standard_responses",
        data=json.dumps({}),
        content_type="application/json",
        headers={
            "X-Original-Request-Uri": "/reverse/standard_responses",
            "Host": "localhost",
        },
    )
    assert response.status_code == 201
    assert response.json == {"status": "Successful"}
    assert (
        response.headers["location"]
        == "http://localhost/reverse/standard_responses?id=43"
    )


def test_standard_delete_response(client):
    response = client.delete("/standard_responses")
    assert response.status_code == 204


def test_generated_swagger(client):
    response = client.get("/swagger.json")
    assert response.status_code == 200
    assert response.json == {
        "swagger": "2.0",
        "basePath": "/",
        "paths": {
            "/standard_responses": {
                "delete": {
                    "responses": {"204": {"description": "Deleted"}},
                    "operationId": "delete_standard_responses",
                    "tags": ["default"],
                },
                "post": {
                    "responses": {
                        "201": {
                            "description": "Created",
                            "headers": {
                                "location": {
                                    "description": "Location of created resource.",
                                    "type": "string",
                                }
                            },
                            "schema": {"$ref": "#/definitions/Created"},
                        }
                    },
                    "operationId": "post_standard_responses",
                    "tags": ["default"],
                },
                "put": {
                    "responses": {
                        "201": {
                            "description": "Updated",
                            "headers": {
                                "location": {
                                    "description": "Location of updated resource.",
                                    "type": "string",
                                }
                            },
                            "schema": {"$ref": "#/definitions/Updated"},
                        }
                    },
                    "operationId": "put_standard_responses",
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
        "definitions": {
            "Created": {
                "properties": {"status": {"default": "Successful", "type": "string"}},
                "type": "object",
            },
            "Updated": {
                "properties": {"status": {"default": "Successful", "type": "string"}},
                "type": "object",
            },
        },
    }
