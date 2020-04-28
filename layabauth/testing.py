import pytest
import layabauth._http
from responses import RequestsMock


@pytest.fixture
def auth_mock(
    monkeypatch, responses: RequestsMock, token_body: dict, identity_provider_url: str
):
    responses.add(method=responses.GET, url=identity_provider_url)
    monkeypatch.setattr(
        layabauth._http.jwt, "decode", lambda *args, **kwargs: token_body
    )
