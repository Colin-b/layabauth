import gzip
import re

import pytest
from flask import Flask, Response, json
from flask_restplus import Resource, Api

from pycommon_server import flask_restplus_common


@pytest.fixture
def app():
    application = Flask(__name__)
    application.testing = True
    api = Api(application)

    @api.route("/requires_authentication")
    class RequiresAuthentication(Resource):
        @flask_restplus_common.requires_authentication
        def get(self):
            return ""

        @flask_restplus_common.requires_authentication
        def post(self):
            return ""

        @flask_restplus_common.requires_authentication
        def put(self):
            return ""

        @flask_restplus_common.requires_authentication
        def delete(self):
            return ""

    @api.route("/logging")
    class Logging(Resource):
        @flask_restplus_common._log_request_details
        def get(self):
            return ""

        @flask_restplus_common._log_request_details
        def post(self):
            return ""

        @flask_restplus_common._log_request_details
        def put(self):
            return ""

        @flask_restplus_common._log_request_details
        def delete(self):
            return ""

    @api.route("/standard_responses")
    class StandardResponses(Resource):
        @api.doc(**flask_restplus_common.created_response_doc(api))
        def post(self):
            return flask_restplus_common.created_response("/standard_responses?id=42")

        @api.doc(**flask_restplus_common.updated_response_doc(api))
        def put(self):
            return flask_restplus_common.updated_response("/standard_responses?id=43")

        @api.response(*flask_restplus_common.deleted_response_doc)
        def delete(self):
            return flask_restplus_common.deleted_response

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
            },
            "/requires_authentication": {
                "delete": {
                    "responses": {"200": {"description": "Success"}},
                    "operationId": "delete_requires_authentication",
                    "tags": ["default"],
                },
                "get": {
                    "responses": {"200": {"description": "Success"}},
                    "operationId": "get_requires_authentication",
                    "tags": ["default"],
                },
                "post": {
                    "responses": {"200": {"description": "Success"}},
                    "operationId": "post_requires_authentication",
                    "tags": ["default"],
                },
                "put": {
                    "responses": {"200": {"description": "Success"}},
                    "operationId": "put_requires_authentication",
                    "tags": ["default"],
                },
            },
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
            },
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


def test_authentication_failure_token_not_provided_on_get(client):
    response = client.get("/requires_authentication")
    assert response.status_code == 401
    assert response.json == {"message": "JWT Token is mandatory."}


def test_authentication_failure_token_not_provided_on_post(client):
    response = client.post("/requires_authentication")
    assert response.status_code == 401
    assert response.json == {"message": "JWT Token is mandatory."}


def test_authentication_failure_token_not_provided_on_put(client):
    response = client.put("/requires_authentication")
    assert response.status_code == 401
    assert response.json == {"message": "JWT Token is mandatory."}


def test_authentication_failure_token_not_provided_on_delete(client):
    response = client.delete("/requires_authentication")
    assert response.status_code == 401
    assert response.json == {"message": "JWT Token is mandatory."}


def test_authentication_failure_fake_token_provided_on_get(client):
    response = client.get(
        "/requires_authentication", headers={"Authorization": "Bearer Fake token"}
    )
    assert response.status_code == 401
    assert response.json == {
        "message": "Invalid JWT Token (header, body and signature must be separated by dots)."
    }


def test_authentication_failure_fake_token_provided_on_post(client):
    response = client.post(
        "/requires_authentication", headers={"Authorization": "Bearer Fake token"}
    )
    assert response.status_code == 401
    assert response.json == {
        "message": "Invalid JWT Token (header, body and signature must be separated by dots)."
    }


def test_authentication_failure_fake_token_provided_on_put(client):
    response = client.put(
        "/requires_authentication", headers={"Authorization": "Bearer Fake token"}
    )
    assert response.status_code == 401
    assert response.json == {
        "message": "Invalid JWT Token (header, body and signature must be separated by dots)."
    }


def test_authentication_failure_fake_token_provided_on_delete(client):
    response = client.delete(
        "/requires_authentication", headers={"Authorization": "Bearer Fake token"}
    )
    assert response.status_code == 401
    assert response.json == {
        "message": "Invalid JWT Token (header, body and signature must be separated by dots)."
    }


def test_authentication_failure_invalid_key_identifier_in_token_on_get(client):
    response = client.get(
        "/requires_authentication",
        headers={
            "Authorization": "Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiIsIng1dCI6IlNTUWRoSTFjS3ZoUUVEU0p4RTJnR1lzNDBRMC"
            "IsImtpZCI6IlNTUWRoSTFjS3ZoUUVEU0p4RTJnR1lzNDBRMCJ9.eyJhdWQiOiIyYmVmNzMzZC03NWJlLTQxNTktYj"
            "I4MC02NzJlMDU0OTM4YzMiLCJpc3MiOiJodHRwczovL3N0cy53aW5kb3dzLm5ldC8yNDEzOWQxNC1jNjJjLTRjNDc"
            "tOGJkZC1jZTcxZWExZDUwY2YvIiwiaWF0IjoxNTIwMjcwNTAxLCJuYmYiOjE1MjAyNzA1MDEsImV4cCI6MTUyMDI3"
            "NDQwMSwiYWlvIjoiWTJOZ1lFaHlXMjYwVS9kR1RGeWNTMWNPVnczYnpqVXQ0Zk96TkNTekJYaWMyWTVOWFFNQSIsI"
            "mFtciI6WyJwd2QiXSwiZmFtaWx5X25hbWUiOiJCb3Vub3VhciIsImdpdmVuX25hbWUiOiJDb2xpbiIsImlwYWRkci"
            "I6IjE5NC4yOS45OC4xNDQiLCJuYW1lIjoiQm91bm91YXIgQ29saW4gKEVOR0lFIEVuZXJneSBNYW5hZ2VtZW50KSI"
            "sIm5vbmNlIjoiW1x1MDAyNzczNjJDQUVBLTlDQTUtNEI0My05QkEzLTM0RDdDMzAzRUJBN1x1MDAyN10iLCJvaWQi"
            "OiJkZTZiOGVjYS01ZTEzLTRhZTEtODcyMS1mZGNmNmI0YTljZGQiLCJvbnByZW1fc2lkIjoiUy0xLTUtMjEtMTQwO"
            "TA4MjIzMy0xNDE3MDAxMzMzLTY4MjAwMzMzMC0zNzY5NTQiLCJzdWIiOiI2eEZSV1FBaElOZ0I4Vy10MnJRVUJzcE"
            "lGc1VyUXQ0UUZ1V1VkSmRxWFdnIiwidGlkIjoiMjQxMzlkMTQtYzYyYy00YzQ3LThiZGQtY2U3MWVhMWQ1MGNmIiw"
            "idW5pcXVlX25hbWUiOiJKUzUzOTFAZW5naWUuY29tIiwidXBuIjoiSlM1MzkxQGVuZ2llLmNvbSIsInV0aSI6InVm"
            "M0x0X1Q5aWsyc0hGQ01oNklhQUEiLCJ2ZXIiOiIxLjAifQ.addwLSoO-2t1kXgljqnaU-P1hQGHQBiJMcNCLwELhB"
            "ZT_vHvkZHFrmgfcTzED_AMdB9mTpvUm_Mk0d3F3RzLtyCeAApOPJaRAwccAc3PB1pKTwjFhdzIXtxib0_MQ6_F1fh"
            "b8R8ZcLCbwhMtT8nXoeWJOvH9_71O_vkfOn6E-VwLo17jkvQJOa89KfctGNnHNMcPBBju0oIgp_UVal311SMUw_10"
            "i4GZZkjR2I1m7EMg5jMwQgUatYWv2J5HoefAQQDat9jJeEnYNITxsJMN81FHTyuvMnN_ulFzOGtcvlBpmP6jVHfED"
            "oJiqFM4NFh6r4IlOs2U2-jUb_bR5xi2zg"
        },
    )
    assert response.status_code == 401
    assert re.match(
        "\{'message': \"SSQdhI1cKvhQEDSJxE2gGYs40Q0 is not a valid key identifier. Valid ones are .*\"\}",
        str(response.json),
    )


def test_authentication_failure_invalid_key_identifier_in_token_on_post(client):
    response = client.post(
        "/requires_authentication",
        headers={
            "Authorization": "Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiIsIng1dCI6IlNTUWRoSTFjS3ZoUUVEU0p4RTJnR1lzNDBRMC"
            "IsImtpZCI6IlNTUWRoSTFjS3ZoUUVEU0p4RTJnR1lzNDBRMCJ9.eyJhdWQiOiIyYmVmNzMzZC03NWJlLTQxNTktYj"
            "I4MC02NzJlMDU0OTM4YzMiLCJpc3MiOiJodHRwczovL3N0cy53aW5kb3dzLm5ldC8yNDEzOWQxNC1jNjJjLTRjNDc"
            "tOGJkZC1jZTcxZWExZDUwY2YvIiwiaWF0IjoxNTIwMjcwNTAxLCJuYmYiOjE1MjAyNzA1MDEsImV4cCI6MTUyMDI3"
            "NDQwMSwiYWlvIjoiWTJOZ1lFaHlXMjYwVS9kR1RGeWNTMWNPVnczYnpqVXQ0Zk96TkNTekJYaWMyWTVOWFFNQSIsI"
            "mFtciI6WyJwd2QiXSwiZmFtaWx5X25hbWUiOiJCb3Vub3VhciIsImdpdmVuX25hbWUiOiJDb2xpbiIsImlwYWRkci"
            "I6IjE5NC4yOS45OC4xNDQiLCJuYW1lIjoiQm91bm91YXIgQ29saW4gKEVOR0lFIEVuZXJneSBNYW5hZ2VtZW50KSI"
            "sIm5vbmNlIjoiW1x1MDAyNzczNjJDQUVBLTlDQTUtNEI0My05QkEzLTM0RDdDMzAzRUJBN1x1MDAyN10iLCJvaWQi"
            "OiJkZTZiOGVjYS01ZTEzLTRhZTEtODcyMS1mZGNmNmI0YTljZGQiLCJvbnByZW1fc2lkIjoiUy0xLTUtMjEtMTQwO"
            "TA4MjIzMy0xNDE3MDAxMzMzLTY4MjAwMzMzMC0zNzY5NTQiLCJzdWIiOiI2eEZSV1FBaElOZ0I4Vy10MnJRVUJzcE"
            "lGc1VyUXQ0UUZ1V1VkSmRxWFdnIiwidGlkIjoiMjQxMzlkMTQtYzYyYy00YzQ3LThiZGQtY2U3MWVhMWQ1MGNmIiw"
            "idW5pcXVlX25hbWUiOiJKUzUzOTFAZW5naWUuY29tIiwidXBuIjoiSlM1MzkxQGVuZ2llLmNvbSIsInV0aSI6InVm"
            "M0x0X1Q5aWsyc0hGQ01oNklhQUEiLCJ2ZXIiOiIxLjAifQ.addwLSoO-2t1kXgljqnaU-P1hQGHQBiJMcNCLwELhB"
            "ZT_vHvkZHFrmgfcTzED_AMdB9mTpvUm_Mk0d3F3RzLtyCeAApOPJaRAwccAc3PB1pKTwjFhdzIXtxib0_MQ6_F1fh"
            "b8R8ZcLCbwhMtT8nXoeWJOvH9_71O_vkfOn6E-VwLo17jkvQJOa89KfctGNnHNMcPBBju0oIgp_UVal311SMUw_10"
            "i4GZZkjR2I1m7EMg5jMwQgUatYWv2J5HoefAQQDat9jJeEnYNITxsJMN81FHTyuvMnN_ulFzOGtcvlBpmP6jVHfED"
            "oJiqFM4NFh6r4IlOs2U2-jUb_bR5xi2zg"
        },
    )
    assert response.status_code == 401
    assert re.match(
        "\{'message': \"SSQdhI1cKvhQEDSJxE2gGYs40Q0 is not a valid key identifier. Valid ones are .*\"\}",
        str(response.json),
    )


def test_authentication_failure_invalid_key_identifier_in_token_on_put(client):
    response = client.put(
        "/requires_authentication",
        headers={
            "Authorization": "Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiIsIng1dCI6IlNTUWRoSTFjS3ZoUUVEU0p4RTJnR1lzNDBRMC"
            "IsImtpZCI6IlNTUWRoSTFjS3ZoUUVEU0p4RTJnR1lzNDBRMCJ9.eyJhdWQiOiIyYmVmNzMzZC03NWJlLTQxNTktYj"
            "I4MC02NzJlMDU0OTM4YzMiLCJpc3MiOiJodHRwczovL3N0cy53aW5kb3dzLm5ldC8yNDEzOWQxNC1jNjJjLTRjNDc"
            "tOGJkZC1jZTcxZWExZDUwY2YvIiwiaWF0IjoxNTIwMjcwNTAxLCJuYmYiOjE1MjAyNzA1MDEsImV4cCI6MTUyMDI3"
            "NDQwMSwiYWlvIjoiWTJOZ1lFaHlXMjYwVS9kR1RGeWNTMWNPVnczYnpqVXQ0Zk96TkNTekJYaWMyWTVOWFFNQSIsI"
            "mFtciI6WyJwd2QiXSwiZmFtaWx5X25hbWUiOiJCb3Vub3VhciIsImdpdmVuX25hbWUiOiJDb2xpbiIsImlwYWRkci"
            "I6IjE5NC4yOS45OC4xNDQiLCJuYW1lIjoiQm91bm91YXIgQ29saW4gKEVOR0lFIEVuZXJneSBNYW5hZ2VtZW50KSI"
            "sIm5vbmNlIjoiW1x1MDAyNzczNjJDQUVBLTlDQTUtNEI0My05QkEzLTM0RDdDMzAzRUJBN1x1MDAyN10iLCJvaWQi"
            "OiJkZTZiOGVjYS01ZTEzLTRhZTEtODcyMS1mZGNmNmI0YTljZGQiLCJvbnByZW1fc2lkIjoiUy0xLTUtMjEtMTQwO"
            "TA4MjIzMy0xNDE3MDAxMzMzLTY4MjAwMzMzMC0zNzY5NTQiLCJzdWIiOiI2eEZSV1FBaElOZ0I4Vy10MnJRVUJzcE"
            "lGc1VyUXQ0UUZ1V1VkSmRxWFdnIiwidGlkIjoiMjQxMzlkMTQtYzYyYy00YzQ3LThiZGQtY2U3MWVhMWQ1MGNmIiw"
            "idW5pcXVlX25hbWUiOiJKUzUzOTFAZW5naWUuY29tIiwidXBuIjoiSlM1MzkxQGVuZ2llLmNvbSIsInV0aSI6InVm"
            "M0x0X1Q5aWsyc0hGQ01oNklhQUEiLCJ2ZXIiOiIxLjAifQ.addwLSoO-2t1kXgljqnaU-P1hQGHQBiJMcNCLwELhB"
            "ZT_vHvkZHFrmgfcTzED_AMdB9mTpvUm_Mk0d3F3RzLtyCeAApOPJaRAwccAc3PB1pKTwjFhdzIXtxib0_MQ6_F1fh"
            "b8R8ZcLCbwhMtT8nXoeWJOvH9_71O_vkfOn6E-VwLo17jkvQJOa89KfctGNnHNMcPBBju0oIgp_UVal311SMUw_10"
            "i4GZZkjR2I1m7EMg5jMwQgUatYWv2J5HoefAQQDat9jJeEnYNITxsJMN81FHTyuvMnN_ulFzOGtcvlBpmP6jVHfED"
            "oJiqFM4NFh6r4IlOs2U2-jUb_bR5xi2zg"
        },
    )
    assert response.status_code == 401
    assert re.match(
        "\{'message': \"SSQdhI1cKvhQEDSJxE2gGYs40Q0 is not a valid key identifier. Valid ones are .*\"\}",
        str(response.json),
    )


def test_authentication_failure_invalid_key_identifier_in_token_on_delete(client):
    response = client.delete(
        "/requires_authentication",
        headers={
            "Authorization": "Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiIsIng1dCI6IlNTUWRoSTFjS3ZoUUVEU0p4RTJnR1lzNDBRMC"
            "IsImtpZCI6IlNTUWRoSTFjS3ZoUUVEU0p4RTJnR1lzNDBRMCJ9.eyJhdWQiOiIyYmVmNzMzZC03NWJlLTQxNTktYj"
            "I4MC02NzJlMDU0OTM4YzMiLCJpc3MiOiJodHRwczovL3N0cy53aW5kb3dzLm5ldC8yNDEzOWQxNC1jNjJjLTRjNDc"
            "tOGJkZC1jZTcxZWExZDUwY2YvIiwiaWF0IjoxNTIwMjcwNTAxLCJuYmYiOjE1MjAyNzA1MDEsImV4cCI6MTUyMDI3"
            "NDQwMSwiYWlvIjoiWTJOZ1lFaHlXMjYwVS9kR1RGeWNTMWNPVnczYnpqVXQ0Zk96TkNTekJYaWMyWTVOWFFNQSIsI"
            "mFtciI6WyJwd2QiXSwiZmFtaWx5X25hbWUiOiJCb3Vub3VhciIsImdpdmVuX25hbWUiOiJDb2xpbiIsImlwYWRkci"
            "I6IjE5NC4yOS45OC4xNDQiLCJuYW1lIjoiQm91bm91YXIgQ29saW4gKEVOR0lFIEVuZXJneSBNYW5hZ2VtZW50KSI"
            "sIm5vbmNlIjoiW1x1MDAyNzczNjJDQUVBLTlDQTUtNEI0My05QkEzLTM0RDdDMzAzRUJBN1x1MDAyN10iLCJvaWQi"
            "OiJkZTZiOGVjYS01ZTEzLTRhZTEtODcyMS1mZGNmNmI0YTljZGQiLCJvbnByZW1fc2lkIjoiUy0xLTUtMjEtMTQwO"
            "TA4MjIzMy0xNDE3MDAxMzMzLTY4MjAwMzMzMC0zNzY5NTQiLCJzdWIiOiI2eEZSV1FBaElOZ0I4Vy10MnJRVUJzcE"
            "lGc1VyUXQ0UUZ1V1VkSmRxWFdnIiwidGlkIjoiMjQxMzlkMTQtYzYyYy00YzQ3LThiZGQtY2U3MWVhMWQ1MGNmIiw"
            "idW5pcXVlX25hbWUiOiJKUzUzOTFAZW5naWUuY29tIiwidXBuIjoiSlM1MzkxQGVuZ2llLmNvbSIsInV0aSI6InVm"
            "M0x0X1Q5aWsyc0hGQ01oNklhQUEiLCJ2ZXIiOiIxLjAifQ.addwLSoO-2t1kXgljqnaU-P1hQGHQBiJMcNCLwELhB"
            "ZT_vHvkZHFrmgfcTzED_AMdB9mTpvUm_Mk0d3F3RzLtyCeAApOPJaRAwccAc3PB1pKTwjFhdzIXtxib0_MQ6_F1fh"
            "b8R8ZcLCbwhMtT8nXoeWJOvH9_71O_vkfOn6E-VwLo17jkvQJOa89KfctGNnHNMcPBBju0oIgp_UVal311SMUw_10"
            "i4GZZkjR2I1m7EMg5jMwQgUatYWv2J5HoefAQQDat9jJeEnYNITxsJMN81FHTyuvMnN_ulFzOGtcvlBpmP6jVHfED"
            "oJiqFM4NFh6r4IlOs2U2-jUb_bR5xi2zg"
        },
    )
    assert response.status_code == 401
    assert re.match(
        "\{'message': \"SSQdhI1cKvhQEDSJxE2gGYs40Q0 is not a valid key identifier. Valid ones are .*\"\}",
        str(response.json),
    )


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


def test_basic_api():
    app, api = flask_restplus_common.create_api(
        __file__,
        title="TestApi",
        description="Testing API",
        cors=False,
        reverse_proxy=False,
    )

    with app.test_client() as client:
        response = client.get("/swagger.json")
        assert response.status_code == 200
        assert response.json == {
            "swagger": "2.0",
            "basePath": "/",
            "paths": {},
            "info": {
                "title": "TestApi",
                "version": "1.0.0",
                "description": "Testing API",
                "x-server-environment": "default",
            },
            "produces": ["application/json"],
            "consumes": ["application/json"],
            "tags": [],
            "responses": {
                "ParseError": {"description": "When a mask can't be parsed"},
                "MaskError": {"description": "When any error occurs on mask"},
            },
        }


def test_cors_api():
    app, api = flask_restplus_common.create_api(
        __file__, title="TestApi", description="Testing API", reverse_proxy=False
    )

    with app.test_client() as client:
        response = client.get("/swagger.json")
        assert response.status_code == 200
        assert response.json == {
            "swagger": "2.0",
            "basePath": "/",
            "paths": {},
            "info": {
                "title": "TestApi",
                "version": "1.0.0",
                "description": "Testing API",
                "x-server-environment": "default",
            },
            "produces": ["application/json"],
            "consumes": ["application/json"],
            "tags": [],
            "responses": {
                "ParseError": {"description": "When a mask can't be parsed"},
                "MaskError": {"description": "When any error occurs on mask"},
            },
        }
        assert response.headers.get("Access-Control-Allow-Origin") == "*"


def test_compress_api():
    app, api = flask_restplus_common.create_api(
        __file__,
        title="TestApi",
        description="Testing API",
        cors=False,
        reverse_proxy=False,
        compress_mimetypes=["application/json"],
    )

    heavy_answer = {"test": 1000 * "A"}

    @api.route("/test")
    class TestRoute(Resource):
        def get(self):
            return Response(
                response=json.dumps(heavy_answer), mimetype="application/json"
            )

    with app.test_client() as client:
        response = client.get("/test", headers=[("Accept-Encoding", "gzip")])
        assert response.status_code == 200
        assert response.content_encoding == "gzip"
        assert (
            json.loads(gzip.decompress(response.data).decode("utf-8")) == heavy_answer
        )


def test_reverse_proxy_api():
    app, api = flask_restplus_common.create_api(
        __file__, title="TestApi", description="Testing API", cors=False
    )

    with app.test_client() as client:
        response = client.get(
            "/swagger.json",
            headers=[("X-Original-Request-Uri", "/behind_reverse_proxy")],
        )
        assert response.status_code == 200
        assert response.json == {
            "swagger": "2.0",
            "basePath": "/behind_reverse_proxy",
            "paths": {},
            "info": {
                "title": "TestApi",
                "version": "1.0.0",
                "description": "Testing API",
                "x-server-environment": "default",
            },
            "produces": ["application/json"],
            "consumes": ["application/json"],
            "tags": [],
            "responses": {
                "ParseError": {"description": "When a mask can't be parsed"},
                "MaskError": {"description": "When any error occurs on mask"},
            },
        }


def test_extra_parameters_api():
    app, api = flask_restplus_common.create_api(
        __file__,
        title="TestApi",
        description="Testing API",
        cors=False,
        reverse_proxy=False,
        license_url="my.license.com",
        license="MIT",
    )

    with app.test_client() as client:
        response = client.get(
            "/swagger.json",
            headers=[("X-Original-Request-Uri", "/behind_reverse_proxy")],
        )
        assert response.status_code == 200
        assert response.json == {
            "swagger": "2.0",
            "basePath": "/",
            "paths": {},
            "info": {
                "title": "TestApi",
                "version": "1.0.0",
                "description": "Testing API",
                "x-server-environment": "default",
                "license": {"name": "MIT", "url": "my.license.com"},
            },
            "produces": ["application/json"],
            "consumes": ["application/json"],
            "tags": [],
            "responses": {
                "ParseError": {"description": "When a mask can't be parsed"},
                "MaskError": {"description": "When any error occurs on mask"},
            },
        }
