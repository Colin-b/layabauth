from collections import namedtuple

import flask
import flask_restplus

import layabauth
from layabauth.mock import *


@pytest.fixture
def app():
    application = flask.Flask(__name__)
    application.testing = True
    api = flask_restplus.Api(application)

    @api.route("/requires_authentication")
    class RequiresAuthentication(flask_restplus.Resource):
        @layabauth.requires_authentication("https://test_identity_provider")
        def get(self):
            return "OK"

        @layabauth.requires_authentication("https://test_identity_provider")
        def post(self):
            return "OK"

        @layabauth.requires_authentication("https://test_identity_provider")
        def put(self):
            return "OK"

        @layabauth.requires_authentication("https://test_identity_provider")
        def delete(self):
            return "OK"

    @api.route("/user_id")
    class UserId(flask_restplus.Resource):
        def get(self):
            record = namedtuple("TestRecord", [])
            layabauth.UserIdFilter().filter(record)
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


def test_authentication_failure_invalid_key_identifier_in_token_on_get(client, responses):
    responses.add(
        responses.GET,
        "https://test_identity_provider",
        json={
            "keys": [
                {
                    "kid": "SSQdhI1cKvhQEDSJxE2gGYs40Q1",
                    "x5c": [
                        "MIIDBTCCAe2gAwIBAgIQdEMOjSqDVbdN3mzb2IumCzANBgkqhkiG9w0BAQsFADAtMSswKQYDVQQDEyJhY2NvdW50cy5hY2Nlc3Njb250cm9sLndpbmRvd3MubmV0MB4XDTE5MDYwNDAwMDAwMFoXDTIxMDYwNDAwMDAwMFowLTErMCkGA1UEAxMiYWNjb3VudHMuYWNjZXNzY29udHJvbC53aW5kb3dzLm5ldDCCASIwDQYJKoZIhvcNAQEBBQADggEPADCCAQoCggEBAKEUUBvom99MdPXlrQ6S9MFmoQPoYI3NJVqEFOJcARY11dj3zyJogL8MTsTRt+DIJ8NyvYbgWC7K7zkAGzHQZhPJcM/AxSjFqh6qB98UqgxoSGBaG0A4lUZJHnKW3qx+YaiWrkg+z4sAwUkP0QgyI29Ejpkk6WUfe1rOJNc/defFUX+AVGxo81beLVAM/8tnCOSbF0H3IADwd76D/Hrp8RsGf4jPHr8N4VDsO/p7oj8rbOx0pL1ehjMK13zspmP8NO5mMcP9i5yiJ37FgbXESAxvja7I9t+y4LQYSu05M7la4Lqv//m5A8MBd6k0VxgF/Sq8GOIbkcQ0bJTCIN9B6oMCAwEAAaMhMB8wHQYDVR0OBBYEFNRP0Lf6MDeL11RDH0uL7H+/JqtLMA0GCSqGSIb3DQEBCwUAA4IBAQCJKR1nxp9Ij/yisCmDG7bdN1yHj/2HdVvyLfCCyReRfkB3cnTZVaIOBy5occGkdmsYJ+q8uqczkoCMAz3gvvq1c0msKEiNpqWNeU2aRXqyL3QZJ/GBmUK1I0tINPVv8j7znm0DcvHHXFvhzS8E4s8ai8vQkcpyac/7Z4PN43HtjDnkZo9Zxm7JahHshrhA8sSPvsuC4dQAcHbOrLbHG+HIo3Tq2pNl7mfQ9fVJ2FxbqlzPYr/rK8H2GTA6N55SuP3KTNvyL3RnMa3hXmGTdG1dpMFzD/IE623h/BqY6j29PyQC/+MUD4UCZ6KW9oIzpi27pKQagH1i1jpBU/ceH6AW"
                    ],
                }
            ]
        },
    )
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
    assert response.json == {'message': "SSQdhI1cKvhQEDSJxE2gGYs40Q0 is not a valid key identifier. Valid ones are ['SSQdhI1cKvhQEDSJxE2gGYs40Q1']."}


def test_authentication_failure_invalid_key_identifier_in_token_on_post(client, responses):
    responses.add(
        responses.GET,
        "https://test_identity_provider",
        json={
            "keys": [
                {
                    "kid": "SSQdhI1cKvhQEDSJxE2gGYs40Q1",
                    "x5c": [
                        "MIIDBTCCAe2gAwIBAgIQdEMOjSqDVbdN3mzb2IumCzANBgkqhkiG9w0BAQsFADAtMSswKQYDVQQDEyJhY2NvdW50cy5hY2Nlc3Njb250cm9sLndpbmRvd3MubmV0MB4XDTE5MDYwNDAwMDAwMFoXDTIxMDYwNDAwMDAwMFowLTErMCkGA1UEAxMiYWNjb3VudHMuYWNjZXNzY29udHJvbC53aW5kb3dzLm5ldDCCASIwDQYJKoZIhvcNAQEBBQADggEPADCCAQoCggEBAKEUUBvom99MdPXlrQ6S9MFmoQPoYI3NJVqEFOJcARY11dj3zyJogL8MTsTRt+DIJ8NyvYbgWC7K7zkAGzHQZhPJcM/AxSjFqh6qB98UqgxoSGBaG0A4lUZJHnKW3qx+YaiWrkg+z4sAwUkP0QgyI29Ejpkk6WUfe1rOJNc/defFUX+AVGxo81beLVAM/8tnCOSbF0H3IADwd76D/Hrp8RsGf4jPHr8N4VDsO/p7oj8rbOx0pL1ehjMK13zspmP8NO5mMcP9i5yiJ37FgbXESAxvja7I9t+y4LQYSu05M7la4Lqv//m5A8MBd6k0VxgF/Sq8GOIbkcQ0bJTCIN9B6oMCAwEAAaMhMB8wHQYDVR0OBBYEFNRP0Lf6MDeL11RDH0uL7H+/JqtLMA0GCSqGSIb3DQEBCwUAA4IBAQCJKR1nxp9Ij/yisCmDG7bdN1yHj/2HdVvyLfCCyReRfkB3cnTZVaIOBy5occGkdmsYJ+q8uqczkoCMAz3gvvq1c0msKEiNpqWNeU2aRXqyL3QZJ/GBmUK1I0tINPVv8j7znm0DcvHHXFvhzS8E4s8ai8vQkcpyac/7Z4PN43HtjDnkZo9Zxm7JahHshrhA8sSPvsuC4dQAcHbOrLbHG+HIo3Tq2pNl7mfQ9fVJ2FxbqlzPYr/rK8H2GTA6N55SuP3KTNvyL3RnMa3hXmGTdG1dpMFzD/IE623h/BqY6j29PyQC/+MUD4UCZ6KW9oIzpi27pKQagH1i1jpBU/ceH6AW"
                    ],
                }
            ]
        },
    )
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
    assert response.json == {'message': "SSQdhI1cKvhQEDSJxE2gGYs40Q0 is not a valid key identifier. Valid ones are ['SSQdhI1cKvhQEDSJxE2gGYs40Q1']."}


def test_authentication_failure_invalid_key_identifier_in_token_on_put(client, responses):
    responses.add(
        responses.GET,
        "https://test_identity_provider",
        json={
            "keys": [
                {
                    "kid": "SSQdhI1cKvhQEDSJxE2gGYs40Q1",
                    "x5c": [
                        "MIIDBTCCAe2gAwIBAgIQdEMOjSqDVbdN3mzb2IumCzANBgkqhkiG9w0BAQsFADAtMSswKQYDVQQDEyJhY2NvdW50cy5hY2Nlc3Njb250cm9sLndpbmRvd3MubmV0MB4XDTE5MDYwNDAwMDAwMFoXDTIxMDYwNDAwMDAwMFowLTErMCkGA1UEAxMiYWNjb3VudHMuYWNjZXNzY29udHJvbC53aW5kb3dzLm5ldDCCASIwDQYJKoZIhvcNAQEBBQADggEPADCCAQoCggEBAKEUUBvom99MdPXlrQ6S9MFmoQPoYI3NJVqEFOJcARY11dj3zyJogL8MTsTRt+DIJ8NyvYbgWC7K7zkAGzHQZhPJcM/AxSjFqh6qB98UqgxoSGBaG0A4lUZJHnKW3qx+YaiWrkg+z4sAwUkP0QgyI29Ejpkk6WUfe1rOJNc/defFUX+AVGxo81beLVAM/8tnCOSbF0H3IADwd76D/Hrp8RsGf4jPHr8N4VDsO/p7oj8rbOx0pL1ehjMK13zspmP8NO5mMcP9i5yiJ37FgbXESAxvja7I9t+y4LQYSu05M7la4Lqv//m5A8MBd6k0VxgF/Sq8GOIbkcQ0bJTCIN9B6oMCAwEAAaMhMB8wHQYDVR0OBBYEFNRP0Lf6MDeL11RDH0uL7H+/JqtLMA0GCSqGSIb3DQEBCwUAA4IBAQCJKR1nxp9Ij/yisCmDG7bdN1yHj/2HdVvyLfCCyReRfkB3cnTZVaIOBy5occGkdmsYJ+q8uqczkoCMAz3gvvq1c0msKEiNpqWNeU2aRXqyL3QZJ/GBmUK1I0tINPVv8j7znm0DcvHHXFvhzS8E4s8ai8vQkcpyac/7Z4PN43HtjDnkZo9Zxm7JahHshrhA8sSPvsuC4dQAcHbOrLbHG+HIo3Tq2pNl7mfQ9fVJ2FxbqlzPYr/rK8H2GTA6N55SuP3KTNvyL3RnMa3hXmGTdG1dpMFzD/IE623h/BqY6j29PyQC/+MUD4UCZ6KW9oIzpi27pKQagH1i1jpBU/ceH6AW"
                    ],
                }
            ]
        },
    )
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
    assert response.json == {'message': "SSQdhI1cKvhQEDSJxE2gGYs40Q0 is not a valid key identifier. Valid ones are ['SSQdhI1cKvhQEDSJxE2gGYs40Q1']."}


def test_authentication_failure_invalid_key_identifier_in_token_on_delete(client, responses):
    responses.add(
        responses.GET,
        "https://test_identity_provider",
        json={
            "keys": [
                {
                    "kid": "SSQdhI1cKvhQEDSJxE2gGYs40Q1",
                    "x5c": [
                        "MIIDBTCCAe2gAwIBAgIQdEMOjSqDVbdN3mzb2IumCzANBgkqhkiG9w0BAQsFADAtMSswKQYDVQQDEyJhY2NvdW50cy5hY2Nlc3Njb250cm9sLndpbmRvd3MubmV0MB4XDTE5MDYwNDAwMDAwMFoXDTIxMDYwNDAwMDAwMFowLTErMCkGA1UEAxMiYWNjb3VudHMuYWNjZXNzY29udHJvbC53aW5kb3dzLm5ldDCCASIwDQYJKoZIhvcNAQEBBQADggEPADCCAQoCggEBAKEUUBvom99MdPXlrQ6S9MFmoQPoYI3NJVqEFOJcARY11dj3zyJogL8MTsTRt+DIJ8NyvYbgWC7K7zkAGzHQZhPJcM/AxSjFqh6qB98UqgxoSGBaG0A4lUZJHnKW3qx+YaiWrkg+z4sAwUkP0QgyI29Ejpkk6WUfe1rOJNc/defFUX+AVGxo81beLVAM/8tnCOSbF0H3IADwd76D/Hrp8RsGf4jPHr8N4VDsO/p7oj8rbOx0pL1ehjMK13zspmP8NO5mMcP9i5yiJ37FgbXESAxvja7I9t+y4LQYSu05M7la4Lqv//m5A8MBd6k0VxgF/Sq8GOIbkcQ0bJTCIN9B6oMCAwEAAaMhMB8wHQYDVR0OBBYEFNRP0Lf6MDeL11RDH0uL7H+/JqtLMA0GCSqGSIb3DQEBCwUAA4IBAQCJKR1nxp9Ij/yisCmDG7bdN1yHj/2HdVvyLfCCyReRfkB3cnTZVaIOBy5occGkdmsYJ+q8uqczkoCMAz3gvvq1c0msKEiNpqWNeU2aRXqyL3QZJ/GBmUK1I0tINPVv8j7znm0DcvHHXFvhzS8E4s8ai8vQkcpyac/7Z4PN43HtjDnkZo9Zxm7JahHshrhA8sSPvsuC4dQAcHbOrLbHG+HIo3Tq2pNl7mfQ9fVJ2FxbqlzPYr/rK8H2GTA6N55SuP3KTNvyL3RnMa3hXmGTdG1dpMFzD/IE623h/BqY6j29PyQC/+MUD4UCZ6KW9oIzpi27pKQagH1i1jpBU/ceH6AW"
                    ],
                }
            ]
        },
    )
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
    assert response.json == {'message': "SSQdhI1cKvhQEDSJxE2gGYs40Q0 is not a valid key identifier. Valid ones are ['SSQdhI1cKvhQEDSJxE2gGYs40Q1']."}


def test_user_id_filter_with_value_not_set_in_header(client):
    response = client.get("/user_id")
    assert response.get_data(as_text=True) == ""


def test_user_id_filter_with_value_set_in_header(client):
    response = client.get("/user_id", headers={"Authorization": "Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiIsIng1dCI6IlNTUWRoSTFjS3ZoUUVEU0p4RTJnR1lzNDBRMC"
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
            "oJiqFM4NFh6r4IlOs2U2-jUb_bR5xi2zg"})
    assert response.get_data(as_text=True) == "JS5391"


def test_user_id_filter_with_value_already_set_in_flask_globals(client, auth_mock):
    client.get("/requires_authentication")

    record = namedtuple("TestRecord", [])
    layabauth.UserIdFilter().filter(record)
    assert record.user_id == "TEST"


def test_user_id_filter_without_flask():
    record = namedtuple("TestRecord", [])
    layabauth.UserIdFilter().filter(record)
    assert record.user_id == ""


@pytest.fixture
def upn():
    return "TEST@email.com"


def test_auth_mock(client, auth_mock):
    response = client.delete("/requires_authentication")
    assert response.status_code == 200
    assert response.get_data(as_text=True) == '"OK"\n'


def test_method_authorizations():
    assert layabauth.method_authorizations("test1", "test2") == {"security": [{"oauth2": ("test1", "test2")}]}


def test_authorizations():
    assert layabauth.authorizations("https://test_auth", test1="test1 desc", test2="test2 desc") == {
        "oauth2": {
            "scopes": {"test1": "test1 desc", "test2": "test2 desc"},
            "flow": "implicit",
            "authorizationUrl": "https://test_auth",
            "type": "oauth2",
        }
    }
