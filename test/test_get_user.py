import re

import pytest

import pycommon_server.jwt_checker as jwt_checker


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
        jwt_checker.get_user(bearer=encoded, no_auth=False)
    assert re.match(
        "Token validation error: a3QN0BZS7s4nN-BdrjbF0Y_LdMM is not a valid key identifier. Valid ones are .*",
        str(exception_info.value),
    )


def test_get_user_no_auth_no_bearer():
    user = jwt_checker.get_user(bearer=None, no_auth=True)
    assert "anonymous" == user


def test_get_user_no_auth_api_key():
    user = jwt_checker.get_user(bearer="SESAME", no_auth=True)
    assert "PARKER" == user


def test_get_user_no_auth_wrong_key():
    with pytest.raises(ValueError) as exception_info:
        jwt_checker.get_user(bearer="TOTO", no_auth=True)
    assert (
        str(exception_info.value)
        == "Token validation error: Invalid JWT Token (header, body and signature must be separated by dots)."
    )


def test_get_user_no_auth_no_br():
    user = jwt_checker.get_user(bearer="SESAME", no_auth=False)
    assert "PARKER" == user
