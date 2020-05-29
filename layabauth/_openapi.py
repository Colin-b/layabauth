from typing import Dict


def authorizations(auth_url: str, scopes: Dict[str, str]) -> dict:
    """
    Return all security definitions.
    Contains only one OAuth2 implicit flow definition.

    :param auth_url: Authorization URL.
    :param scopes: All scopes that should be available (scope_name = 'description as a string').
    """
    return {
        "oauth2": {
            "scopes": scopes,
            "flow": "implicit",
            "authorizationUrl": auth_url,
            "type": "oauth2",
        }
    }


def method_authorizations(*scopes: str) -> dict:
    """
    Return method security.
    Contains only one OAuth2 security.

    :param scopes: All scope names that should be available (as string).
    """
    return {"security": [{"oauth2": scopes}]}
