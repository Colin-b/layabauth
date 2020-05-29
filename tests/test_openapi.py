import layabauth


def test_method_authorizations():
    assert layabauth.method_authorizations("t,e-st.1", "test2") == {
        "security": [{"oauth2": ("t,e-st.1", "test2")}]
    }


def test_authorizations():
    assert layabauth.authorizations(
        "https://test_auth", scopes={"t,e-st.1": "test1 desc", "test2": "test2 desc"}
    ) == {
        "oauth2": {
            "scopes": {"t,e-st.1": "test1 desc", "test2": "test2 desc"},
            "flow": "implicit",
            "authorizationUrl": "https://test_auth",
            "type": "oauth2",
        }
    }
