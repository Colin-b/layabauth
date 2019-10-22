import pytest
import oauth2helper


@pytest.fixture
def auth_mock(monkeypatch, upn):
    monkeypatch.setattr(oauth2helper, "validate", lambda token, provider_url: ({}, {"upn": upn}))
