from collections import namedtuple

import flask
import flask_restx
import httpx
import flask.testing

import layabauth.flask
from layabauth.testing import *


@pytest.fixture
def app() -> flask.Flask:
    application = flask.Flask(__name__)
    application.testing = True
    api = flask_restx.Api(application)

    @api.route("/requires_authentication")
    class RequiresAuthentication(flask_restx.Resource):
        @layabauth.flask.requires_authentication("https://test_identity_provider")
        def get(self):
            return flask.g.token_body

        @layabauth.flask.requires_authentication("https://test_identity_provider")
        def post(self):
            return flask.g.token_body

        @layabauth.flask.requires_authentication("https://test_identity_provider")
        def put(self):
            return flask.g.token_body

        @layabauth.flask.requires_authentication("https://test_identity_provider")
        def delete(self):
            return flask.g.token_body

    @api.route("/requires_scopes")
    class RequiresScopes(flask_restx.Resource):
        @layabauth.flask.requires_authentication("https://test_identity_provider")
        def get(self):
            layabauth.flask.requires_scopes(
                lambda token, token_body: token_body["scopes"], "scope1", "scope2"
            )
            return flask.g.token_body

        @layabauth.flask.requires_authentication("https://test_identity_provider")
        def post(self):
            layabauth.flask.requires_scopes(
                lambda token, token_body: token_body["scopes"], "scope1"
            )
            return flask.g.token_body

        @layabauth.flask.requires_authentication("https://test_identity_provider")
        def put(self):
            layabauth.flask.requires_scopes(
                lambda token, token_body: token_body["scopes"]
            )
            return flask.g.token_body

        @layabauth.flask.requires_authentication("https://test_identity_provider")
        def delete(self):
            layabauth.flask.requires_scopes(
                lambda token, token_body: token_body["scopes"], "sc.op-e1", "scope2"
            )
            return flask.g.token_body

    @api.route("/user_id")
    class UserId(flask_restx.Resource):
        def get(self):
            record = namedtuple("TestRecord", [])
            layabauth.flask.UserIdFilter("upn").filter(record)
            return flask.make_response(str(record.user_id))

    return application


def test_generated_swagger(client: flask.testing.FlaskClient):
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
            "/requires_scopes": {
                "delete": {
                    "responses": {"200": {"description": "Success"}},
                    "operationId": "delete_requires_scopes",
                    "tags": ["default"],
                },
                "get": {
                    "responses": {"200": {"description": "Success"}},
                    "operationId": "get_requires_scopes",
                    "tags": ["default"],
                },
                "post": {
                    "responses": {"200": {"description": "Success"}},
                    "operationId": "post_requires_scopes",
                    "tags": ["default"],
                },
                "put": {
                    "responses": {"200": {"description": "Success"}},
                    "operationId": "put_requires_scopes",
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


@pytest.mark.parametrize("method", ["GET", "POST", "PUT", "DELETE"])
def test_without_authentication_header(client: flask.testing.FlaskClient, method: str):
    response = client.open(method=method, path="/requires_authentication")
    assert response.status_code == 401
    assert response.json == {
        "message": "The server could not verify that you are authorized to access the URL requested. You either supplied the wrong credentials (e.g. a bad password), or your browser doesn't understand how to supply the credentials required."
    }


@pytest.mark.parametrize("method", ["GET", "POST", "PUT", "DELETE"])
def test_with_non_jwt(client: flask.testing.FlaskClient, httpx_mock, method: str):
    httpx_mock.add_response(method="GET", url="https://test_identity_provider")
    response = client.open(
        method=method,
        path="/requires_authentication",
        headers={"Authorization": "Bearer Fake token"},
    )
    assert response.status_code == 401
    assert response.json == {"message": "Not enough segments"}


@pytest.mark.parametrize("method", ["GET", "POST", "PUT", "DELETE"])
def test_with_invalid_jwt(client: flask.testing.FlaskClient, httpx_mock, method: str):
    httpx_mock.add_response(
        method="GET",
        url="https://test_identity_provider",
        json={
            "keys": [
                {
                    "kty": "RSA",
                    "use": "sig",
                    "kid": "CtTuhMJmD5M7DLdzD2v2x3QKSRY",
                    "x5t": "CtTuhMJmD5M7DLdzD2v2x3QKSRY",
                    "n": "18uZ3P3IgOySlnOsxeIN5WUKzvlm6evPDMFbmXPtTF0GMe7tD2JPfai2UGn74s7AFwqxWO5DQZRu6VfQUux8uMR4J7nxm1Kf__7pVEVJJyDuL5a8PARRYQtH68w-0IZxcFOkgsSdhtIzPQ2jj4mmRzWXIwh8M_8pJ6qiOjvjF9bhEq0CC_f27BnljPaFn8hxY69pCoxenWWqFcsUhFZvCMthhRubAbBilDr74KaXS5xCgySBhPzwekD9_NdCUuCsdqavd4T-VWnbplbB8YsC-R00FptBFKuTyT9zoGZjWZilQVmj7v3k8jXqYB2nWKgTAfwjmiyKz78FHkaE-nCIDw",
                    "e": "AQAB",
                    "x5c": [
                        "MIIDBTCCAe2gAwIBAgIQXVogj9BAf49IpuOSIvztNDANBgkqhkiG9w0BAQsFADAtMSswKQYDVQQDEyJhY2NvdW50cy5hY2Nlc3Njb250cm9sLndpbmRvd3MubmV0MB4XDTIwMDMxNzAwMDAwMFoXDTI1MDMxNzAwMDAwMFowLTErMCkGA1UEAxMiYWNjb3VudHMuYWNjZXNzY29udHJvbC53aW5kb3dzLm5ldDCCASIwDQYJKoZIhvcNAQEBBQADggEPADCCAQoCggEBANfLmdz9yIDskpZzrMXiDeVlCs75ZunrzwzBW5lz7UxdBjHu7Q9iT32otlBp++LOwBcKsVjuQ0GUbulX0FLsfLjEeCe58ZtSn//+6VRFSScg7i+WvDwEUWELR+vMPtCGcXBTpILEnYbSMz0No4+Jpkc1lyMIfDP/KSeqojo74xfW4RKtAgv39uwZ5Yz2hZ/IcWOvaQqMXp1lqhXLFIRWbwjLYYUbmwGwYpQ6++Cml0ucQoMkgYT88HpA/fzXQlLgrHamr3eE/lVp26ZWwfGLAvkdNBabQRSrk8k/c6BmY1mYpUFZo+795PI16mAdp1ioEwH8I5osis+/BR5GhPpwiA8CAwEAAaMhMB8wHQYDVR0OBBYEFF8MDGklOGhGNVJvsHHRCaqtzexcMA0GCSqGSIb3DQEBCwUAA4IBAQCKkegw/mdpCVl1lOpgU4G9RT+1gtcPqZK9kpimuDggSJju6KUQlOCi5/lIH5DCzpjFdmG17TjWVBNve5kowmrhLzovY0Ykk7+6hYTBK8dNNSmd4SK7zY++0aDIuOzHP2Cur+kgFC0gez50tPzotLDtMmp40gknXuzltwJfezNSw3gLgljDsGGcDIXK3qLSYh44qSuRGwulcN2EJUZBI9tIxoODpaWHIN8+z2uZvf8JBYFjA3+n9FRQn51X16CTcjq4QRTbNVpgVuQuyaYnEtx0ZnDvguB3RjGSPIXTRBkLl2x7e8/6uAZ6tchw8rhcOtPsFgJuoJokGjvcUSR/6Eqd"
                    ],
                },
                {
                    "kty": "RSA",
                    "use": "sig",
                    "kid": "SsZsBNhZcF3Q9S4trpQBTByNRRI",
                    "x5t": "SsZsBNhZcF3Q9S4trpQBTByNRRI",
                    "n": "uHPewhg4WC3eLVPkEFlj7RDtaKYWXCI5G-LPVzsMKOuIu7qQQbeytIA6P6HT9_iIRt8zNQvuw4P9vbNjgUCpI6vfZGsjk3XuCVoB_bAIhvuBcQh9ePH2yEwS5reR-NrG1PsqzobnZZuigKCoDmuOb_UDx1DiVyNCbMBlEG7UzTQwLf5NP6HaRHx027URJeZvPAWY7zjHlSOuKoS_d1yUveaBFIgZqPWLCg44ck4gvik45HsNVWT9zYfT74dvUSSrMSR-SHFT7Hy1XjbVXpHJHNNAXpPoGoWXTuc0BxMsB4cqjfJqoftFGOG4x32vEzakArLPxAKwGvkvu0jToAyvSQ",
                    "e": "AQAB",
                    "x5c": [
                        "MIIDBTCCAe2gAwIBAgIQWHw7h/Ysh6hPcXpnrJ0N8DANBgkqhkiG9w0BAQsFADAtMSswKQYDVQQDEyJhY2NvdW50cy5hY2Nlc3Njb250cm9sLndpbmRvd3MubmV0MB4XDTIwMDQyNzAwMDAwMFoXDTI1MDQyNzAwMDAwMFowLTErMCkGA1UEAxMiYWNjb3VudHMuYWNjZXNzY29udHJvbC53aW5kb3dzLm5ldDCCASIwDQYJKoZIhvcNAQEBBQADggEPADCCAQoCggEBALhz3sIYOFgt3i1T5BBZY+0Q7WimFlwiORviz1c7DCjriLu6kEG3srSAOj+h0/f4iEbfMzUL7sOD/b2zY4FAqSOr32RrI5N17glaAf2wCIb7gXEIfXjx9shMEua3kfjaxtT7Ks6G52WbooCgqA5rjm/1A8dQ4lcjQmzAZRBu1M00MC3+TT+h2kR8dNu1ESXmbzwFmO84x5UjriqEv3dclL3mgRSIGaj1iwoOOHJOIL4pOOR7DVVk/c2H0++Hb1EkqzEkfkhxU+x8tV421V6RyRzTQF6T6BqFl07nNAcTLAeHKo3yaqH7RRjhuMd9rxM2pAKyz8QCsBr5L7tI06AMr0kCAwEAAaMhMB8wHQYDVR0OBBYEFOI7M+DDFMlP7Ac3aomPnWo1QL1SMA0GCSqGSIb3DQEBCwUAA4IBAQBv+8rBiDY8sZDBoUDYwFQM74QjqCmgNQfv5B0Vjwg20HinERjQeH24uAWzyhWN9++FmeY4zcRXDY5UNmB0nJz7UGlprA9s7voQ0Lkyiud0DO072RPBg38LmmrqoBsLb3MB9MZ2CGBaHftUHfpdTvrgmXSP0IJn7mCUq27g+hFk7n/MLbN1k8JswEODIgdMRvGqN+mnrPKkviWmcVAZccsWfcmS1pKwXqICTKzd6WmVdz+cL7ZSd9I2X0pY4oRwauoE2bS95vrXljCYgLArI3XB2QcnglDDBRYu3Z3aIJb26PTIyhkVKT7xaXhXl4OgrbmQon9/O61G2dzpjzzBPqNP"
                    ],
                },
                {
                    "kty": "RSA",
                    "use": "sig",
                    "kid": "M6pX7RHoraLsprfJeRCjSxuURhc",
                    "x5t": "M6pX7RHoraLsprfJeRCjSxuURhc",
                    "n": "xHScZMPo8FifoDcrgncWQ7mGJtiKhrsho0-uFPXg-OdnRKYudTD7-Bq1MDjcqWRf3IfDVjFJixQS61M7wm9wALDj--lLuJJ9jDUAWTA3xWvQLbiBM-gqU0sj4mc2lWm6nPfqlyYeWtQcSC0sYkLlayNgX4noKDaXivhVOp7bwGXq77MRzeL4-9qrRYKjuzHfZL7kNBCsqO185P0NI2Jtmw-EsqYsrCaHsfNRGRrTvUHUq3hWa859kK_5uNd7TeY2ZEwKVD8ezCmSfR59ZzyxTtuPpkCSHS9OtUvS3mqTYit73qcvprjl3R8hpjXLb8oftfpWr3hFRdpxrwuoQEO4QQ",
                    "e": "AQAB",
                    "x5c": [
                        "MIIC8TCCAdmgAwIBAgIQfEWlTVc1uINEc9RBi6qHMjANBgkqhkiG9w0BAQsFADAjMSEwHwYDVQQDExhsb2dpbi5taWNyb3NvZnRvbmxpbmUudXMwHhcNMTgxMDE0MDAwMDAwWhcNMjAxMDE0MDAwMDAwWjAjMSEwHwYDVQQDExhsb2dpbi5taWNyb3NvZnRvbmxpbmUudXMwggEiMA0GCSqGSIb3DQEBAQUAA4IBDwAwggEKAoIBAQDEdJxkw+jwWJ+gNyuCdxZDuYYm2IqGuyGjT64U9eD452dEpi51MPv4GrUwONypZF/ch8NWMUmLFBLrUzvCb3AAsOP76Uu4kn2MNQBZMDfFa9AtuIEz6CpTSyPiZzaVabqc9+qXJh5a1BxILSxiQuVrI2BfiegoNpeK+FU6ntvAZervsxHN4vj72qtFgqO7Md9kvuQ0EKyo7Xzk/Q0jYm2bD4SypiysJoex81EZGtO9QdSreFZrzn2Qr/m413tN5jZkTApUPx7MKZJ9Hn1nPLFO24+mQJIdL061S9LeapNiK3vepy+muOXdHyGmNctvyh+1+laveEVF2nGvC6hAQ7hBAgMBAAGjITAfMB0GA1UdDgQWBBQ5TKadw06O0cvXrQbXW0Nb3M3h/DANBgkqhkiG9w0BAQsFAAOCAQEAI48JaFtwOFcYS/3pfS5+7cINrafXAKTL+/+he4q+RMx4TCu/L1dl9zS5W1BeJNO2GUznfI+b5KndrxdlB6qJIDf6TRHh6EqfA18oJP5NOiKhU4pgkF2UMUw4kjxaZ5fQrSoD9omjfHAFNjradnHA7GOAoF4iotvXDWDBWx9K4XNZHWvD11Td66zTg5IaEQDIZ+f8WS6nn/98nAVMDtR9zW7Te5h9kGJGfe6WiHVaGRPpBvqC4iypGHjbRwANwofZvmp5wP08hY1CsnKY5tfP+E2k/iAQgKKa6QoxXToYvP7rsSkglak8N5g/+FJGnq4wP6cOzgZpjdPMwaVt5432GA=="
                    ],
                },
            ]
        },
    )
    response = client.open(
        method=method,
        path="/requires_authentication",
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
    assert response.json == {"message": "Signature verification failed."}


def test_user_id_filter_with_value_not_set_in_header(client):
    response = client.get("/user_id")
    assert response.get_data(as_text=True) == ""


def test_user_id_filter_with_value_set_in_header(client):
    response = client.get(
        "/user_id",
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
    assert response.get_data(as_text=True) == "JS5391@engie.com"


def test_user_id_filter_with_invalid_value_set_in_header(client):
    response = client.get("/user_id", headers={"Authorization": "Bearer my_token"})
    assert response.get_data(as_text=True) == ""


def test_user_id_filter_with_value_already_set_in_flask_globals(
    client: flask.testing.FlaskClient, auth_mock
):
    client.get("/requires_authentication", headers={"Authorization": "Bearer my_token"})

    record = namedtuple("TestRecord", [])
    layabauth.flask.UserIdFilter("upn").filter(record)
    assert record.user_id == "TEST@email.com"


def test_user_id_filter_without_flask():
    record = namedtuple("TestRecord", [])
    layabauth.flask.UserIdFilter("upn").filter(record)
    assert record.user_id == ""


@pytest.fixture
def jwks_uri():
    return "https://test_identity_provider"


@pytest.fixture
def token_body():
    return {"upn": "TEST@email.com", "scopes": ["scope2", "sc.op-e1", "scope1"]}


@pytest.mark.parametrize("method", ["GET", "POST", "PUT", "DELETE"])
def test_auth_mock(client: flask.testing.FlaskClient, auth_mock, method: str):
    response = client.open(
        method=method,
        path="/requires_authentication",
        headers={"Authorization": "Bearer my_token"},
    )
    assert response.status_code == 200
    assert response.json == {
        "upn": "TEST@email.com",
        "scopes": ["scope2", "sc.op-e1", "scope1"],
    }


@pytest.mark.parametrize("method", ["GET", "POST", "PUT", "DELETE"])
def test_auth_mock_scopes(client: flask.testing.FlaskClient, auth_mock, method: str):
    response = client.open(
        method=method,
        path="/requires_scopes",
        headers={"Authorization": "Bearer my_token"},
    )
    assert response.status_code == 200
    assert response.json == {
        "upn": "TEST@email.com",
        "scopes": ["scope2", "sc.op-e1", "scope1"],
    }


def test_keys_cannot_be_retrieved_due_to_network_failure(
    client: flask.testing.FlaskClient, httpx_mock
):
    def raise_exception(request, *args, **kwargs):
        raise httpx.TimeoutException("description", request=request)

    httpx_mock.add_callback(
        method="GET", url="https://test_identity_provider", callback=raise_exception
    )
    response = client.get(
        "/requires_authentication", headers={"Authorization": "Bearer my_token"}
    )
    assert response.status_code == 401
    assert response.json == {
        "message": "TimeoutException error while retrieving keys: description"
    }


def test_keys_cannot_be_retrieved_due_to_http_failure(
    client: flask.testing.FlaskClient, httpx_mock
):
    httpx_mock.add_response(
        method="GET",
        url="https://test_identity_provider",
        status_code=500,
        content=b"description",
    )
    response = client.get(
        "/requires_authentication", headers={"Authorization": "Bearer my_token"}
    )
    assert response.status_code == 401
    assert response.json == {
        "message": "HTTP 500 error while retrieving keys: description"
    }
