from typing import Mapping

import oauth2helper


class User:
    def __init__(self, decoded_body: dict):
        self.name = oauth2helper.user_name(decoded_body)


def authorizations(auth_url, **scopes) -> dict:
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


def method_authorizations(*scopes) -> dict:
    """
    Return method security.
    Contains only one OAuth2 security.

    :param scopes: All scope names that should be available (as string).
    """
    return {"security": [{"oauth2": scopes}]}


def _to_user(token: str, identity_provider_url: str) -> User:
    json_header, json_body = oauth2helper.validate(token, identity_provider_url)
    return User(json_body)


def _get_token(headers: Mapping[str, str]):
    authorization = headers.get("Authorization")
    if authorization and authorization.startswith("Bearer "):
        return authorization[7:]
