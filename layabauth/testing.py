import pytest
import layabauth._http
from responses import RequestsMock


@pytest.fixture
def auth_mock(monkeypatch, responses: RequestsMock, token_body: dict, jwks_uri: str):
    # Mock keys
    responses.add(method=responses.GET, url=jwks_uri)
    # Mock token validation (TODO only deactivate validation so that clients can use raw tokens)
    monkeypatch.setattr(
        layabauth._http.jwt, "decode", lambda *args, **kwargs: token_body
    )
