import re
import collections

import pytest
import flask
import flask_restplus

from pycommon_server import authentication


def test_get_user_bearer():
    encoded = u"""eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiIsIng1dCI6ImEzUU4wQlpTN3M0bk4tQmRyamJGMFlfTGRNTSIsImtpZCI6ImEzUU4wQ
    lpTN3M0bk4tQmRyamJGMFlfTGRNTSJ9.eyJhdWQiOiIyYmVmNzMzZC03NWJlLTQxNTktYjI4MC02NzJlMDU0OTM4YzMiLCJpc3MiOiJodHRwczovL3N0cy5
    3aW5kb3dzLm5ldC8yNDEzOWQxNC1jNjJjLTRjNDctOGJkZC1jZTcxZWExZDUwY2YvIiwiaWF0IjoxNDkwNzc5NzEyLCJuYmYiOjE0OTA3Nzk3MTIsImV4cC
    I6MTQ5MDc4MzYxMiwiYW1yIjpbInB3ZCJdLCJmYW1pbHlfbmFtZSI6IkRlIE1hZXllciIsImdpdmVuX25hbWUiOiJGYWJyaWNlIiwiaXBhZGRyIjoiMTA0L
    jQ2LjU4LjE0OSIsIm5hbWUiOiJEZSBNYWV5ZXIgRmFicmljZSAoZXh0ZXJuYWwpIiwibm9uY2UiOiI3MzYyQ0FFQS05Q0E1LTRCNDMtOUJBMy0zNEQ3QzMw
    M0VCQTciLCJvaWQiOiI1YTJmOGQyYS0xNzQ1LTRmNTctOTcwYS03YjIwMzU5YWUyZGMiLCJvbnByZW1fc2lkIjoiUy0xLTUtMjEtMTQwOTA4MjIzMy0xNDE
    3MDAxMzMzLTY4MjAwMzMzMC0yODUxNjAiLCJwbGF0ZiI6IjMiLCJzdWIiOiJRcjhNZlAwQk9oRld3WlNoNFZSVEpYeGd3Z19XTFBId193TnBnS1lMQTJVIi
    widGlkIjoiMjQxMzlkMTQtYzYyYy00YzQ3LThiZGQtY2U3MWVhMWQ1MGNmIiwidW5pcXVlX25hbWUiOiJCSUY1OTBAZW5naWUuY29tIiwidXBuIjoiQklGN
    TkwQGVuZ2llLmNvbSIsInZlciI6IjEuMCJ9.vZO7a5Vs0G_g92Bb00BPKcLuF9WmrqfLjwbLhz8xEe3OfqfthWHqh_jzf_Md88INc4ZuMqOMPhWZTZjQMgC
    ACIpTiHDpFRkokZ-jqC09BaQSSjwV_27b-zy-m6CZcFtdUe10LIBQEqiL9JnZlVIrBgFqr49bKBvZKr3uuaoeiuR2XcC0U2klYkDr3CYIexX0w57lvD5Ow0
    xKkdWKYVswcJipenU9PP63R0wNXr-8cb-6PGIUzaQDREo-EuR2e3uShF9u5cagG7emt9fDmJr8eGxBJU9ppRoffJpuaYeJiIg1F_n0iK7hENnIjZVnHjFn4
    6DZO-RPse8YZjd4YBuKsg"""

    with pytest.raises(ValueError) as exception_info:
        authentication.get_user(bearer=encoded, no_auth=False)
    assert re.match(
        "Token validation error: a3QN0BZS7s4nN-BdrjbF0Y_LdMM is not a valid key identifier. Valid ones are .*",
        str(exception_info.value),
    )


def test_get_user_no_auth_no_bearer():
    user = authentication.get_user(bearer=None, no_auth=True)
    assert "anonymous" == user


def test_get_user_no_auth_api_key():
    user = authentication.get_user(bearer="SESAME", no_auth=True)
    assert "PARKER" == user


def test_get_user_no_auth_wrong_key():
    with pytest.raises(ValueError) as exception_info:
        authentication.get_user(bearer="TOTO", no_auth=True)
    assert (
        str(exception_info.value)
        == "Token validation error: Invalid JWT Token (header, body and signature must be separated by dots)."
    )


def test_get_user_no_auth_no_br():
    user = authentication.get_user(bearer="SESAME", no_auth=False)
    assert "PARKER" == user


@pytest.fixture
def app():
    application = flask.Flask(__name__)
    application.testing = True
    api = flask_restplus.Api(application)

    @api.route("/requires_authentication")
    class RequiresAuthentication(flask_restplus.Resource):
        @authentication.requires_authentication
        def get(self):
            return ""

        @authentication.requires_authentication
        def post(self):
            return ""

        @authentication.requires_authentication
        def put(self):
            return ""

        @authentication.requires_authentication
        def delete(self):
            return ""

    @api.route("/user_id")
    class UserId(flask_restplus.Resource):
        def get(self):
            record = collections.namedtuple("TestRecord", [])
            authentication.UserIdFilter().filter(record)
            return flask.make_response(str(record.user_id))

    return application


def test_generated_swagger(client):
    response = client.get("/swagger.json")
    assert response.status_code == 200
    assert response.json == {
        "swagger": "2.0",
        "basePath": "/",
        "paths": {
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
            "/user_id": {
                "get": {
                    "operationId": "get_user_id",
                    "responses": {"200": {"description": "Success"}},
                    "tags": ["default"],
                }
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


def test_user_id_filter_with_value_not_set_in_header(client):
    response = client.get("/user_id")
    assert response.get_data(as_text=True) == "anonymous"


def test_user_id_filter_with_value_already_set_in_flask_globals(client):
    client.get("/user_id", headers={"Bearer": "sesame"})
    response = client.get("/user_id")
    assert response.get_data(as_text=True) == "PARKER"


def test_user_id_filter_without_flask():
    record = collections.namedtuple("TestRecord", [])
    authentication.UserIdFilter().filter(record)
    assert record.user_id == ""
