import pytest
import oauth2helper


@pytest.fixture
def auth_mock(monkeypatch, token_body: dict):
    monkeypatch.setattr(
        oauth2helper, "validate", lambda token, provider_url: ({}, token_body)
    )
