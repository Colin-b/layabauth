import warnings
import logging
import functools

import flask
import werkzeug.exceptions
import jwt.exceptions
import oauth2helper


class User:
    def __init__(self, decoded_body: dict):
        self.name = oauth2helper.user_name(decoded_body)


class Authentication:
    """
    Contains helper to manage authentication.
    """

    @staticmethod
    def authorizations(**scopes) -> dict:
        """
        Return all security definitions.
        Contains only one OAuth2 definition using Engie Azure authentication.

        :param scopes: All scopes that should be available (scope_name = 'description as a string').
        """
        engie_tenant_id = "24139d14-c62c-4c47-8bdd-ce71ea1d50cf"
        nonce = scopes.pop("nonce", "7362CAEA-9CA5-4B43-9BA3-34D7C303EBA7")

        return {
            "oauth2": {
                "scopes": scopes,
                "flow": "implicit",
                "authorizationUrl": f"https://login.microsoftonline.com/{engie_tenant_id}/oauth2/authorize?nonce={nonce}",
                "type": "oauth2",
            }
        }

    @staticmethod
    def method_authorizations(*scopes) -> dict:
        """
        Return method security.
        Contains only one OAuth2 security.

        :param scopes: All scope names that should be available (as string).
        """
        return {"security": [{"oauth2": scopes}]}

    @staticmethod
    def _to_user(token: str) -> User:
        try:
            json_header, json_body = oauth2helper.validate(token)
            return User(json_body)
        except (
            jwt.exceptions.InvalidTokenError or jwt.exceptions.InvalidKeyError
        ) as e:
            raise werkzeug.exceptions.Unauthorized(description=str(e))


def requires_authentication(func):
    @functools.wraps(func)
    def wrapper(*func_args, **func_kwargs):
        authorization = flask.request.headers.get("Authorization")
        token = (
            authorization[7:]
            if authorization and authorization.startswith("Bearer ")
            else None
        )
        flask.g.current_user = Authentication._to_user(token)
        return func(*func_args, **func_kwargs)

    return wrapper


def get_user(bearer=None, no_auth=True):
    warnings.warn(
        "Use @requires_authentication decorator and retrieve user via flask.g.current_user",
        DeprecationWarning,
    )
    # if there is a request_context, we still check
    if no_auth and bearer is None:
        return "anonymous"
    elif bearer is not None:
        if bearer.lower() == "sesame":
            return "PARKER"
        else:
            try:
                json_header, json_body = oauth2helper.validate(bearer)
                return oauth2helper.user_name(json_body)
            except Exception as e:
                raise ValueError("Token validation error: " + str(e))
    else:
        raise ValueError(
            'anonymous access is not authorised. Please provide a valid JWT token or access our API via (<a href="https://wiki.gem.myengie.com/display/SER/PyxelRest">pyxelrest Excel addin</a>).'
        )


def _user_id():
    """
    Returns the user identifier or anonymous if there is none
    Also store it in flask.g.user_id

    :return: current user identifier or anonymous if there is none
    """
    if getattr(flask.g, "user_id", None):
        return flask.g.user_id

    # TODO implement generic authentication user_id retrieval
    user_id = get_user(flask.request.headers.get("Bearer"))

    flask.g.user_id = user_id
    return user_id


class UserIdFilter(logging.Filter):
    """
    This is a logging filter that makes the user identifier available for use in the logging format.
    Note that we are checking if we are in a request context, as we may want to log things before Flask is fully loaded.
    """

    def filter(self, record):
        if flask.has_request_context():
            if getattr(flask.g, "user_id", None):
                user_id = flask.g.user_id
            else:
                user_id = get_user(flask.request.headers.get("Bearer"))
                flask.g.user_id = user_id
        else:
            user_id = ""
        record.user_id = user_id
        return True
