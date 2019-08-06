import logging
import functools
from typing import Optional

import flask
import werkzeug.exceptions
import jwt.exceptions
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
    try:
        json_header, json_body = oauth2helper.validate(token, identity_provider_url)
        return User(json_body)
    except (
        jwt.exceptions.InvalidTokenError or jwt.exceptions.InvalidKeyError
    ) as e:
        raise werkzeug.exceptions.Unauthorized(description=str(e))


def _get_token():
    authorization = flask.request.headers.get("Authorization")
    if authorization and authorization.startswith("Bearer "):
        return authorization[7:]


def requires_authentication(identity_provider_url: str):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*func_args, **func_kwargs):
            flask.g.current_user = _to_user(_get_token(), identity_provider_url)
            return func(*func_args, **func_kwargs)

        return wrapper
    return decorator


def _extract_user_name() -> Optional[str]:
    if getattr(flask.g, "current_user", None):
        return flask.g.current_user.name
    try:
        json_header, json_body = oauth2helper.decode(_get_token())
        return User(json_body).name
    except:
        return ""


class UserIdFilter(logging.Filter):
    """
    This is a logging filter that makes the user identifier available for use in the logging format.
    Note that we are checking if we are in a request context, as we may want to log things before Flask is fully loaded.
    """

    def filter(self, record):
        record.user_id = _extract_user_name() if flask.has_request_context() else ""
        return True
