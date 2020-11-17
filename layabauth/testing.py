import pytest
import layabauth._http


@pytest.fixture
def auth_mock(monkeypatch, token_body: dict, jwks_uri: str):
    # Mock keys
    def keys_mock(client, uri):
        assert (
            uri == jwks_uri
        ), f"The mocked JWKS URI does not match the one used by project: {jwks_uri} != {uri}"

    monkeypatch.setattr(layabauth._http, "keys", keys_mock)

    # Mock token validation (TODO only deactivate validation so that clients can use raw tokens)
    monkeypatch.setattr(
        layabauth._http.jwt, "decode", lambda *args, **kwargs: token_body
    )
