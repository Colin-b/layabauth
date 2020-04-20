import layabauth


def test_method_authorizations():
    assert layabauth.method_authorizations("test1", "test2") == {
        "security": [{"oauth2": ("test1", "test2")}]
    }


def test_authorizations():
    assert layabauth.authorizations(
        "https://test_auth", test1="test1 desc", test2="test2 desc"
    ) == {
        "oauth2": {
            "scopes": {"test1": "test1 desc", "test2": "test2 desc"},
            "flow": "implicit",
            "authorizationUrl": "https://test_auth",
            "type": "oauth2",
        }
    }
