import logging
import functools

import flask
import werkzeug
import jwt
import oauth2helper

from layabauth._http import _get_token


def requires_authentication(identity_provider_url: str):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*func_args, **func_kwargs):
            try:
                flask.g.token = _get_token(flask.request.headers)
                json_header, flask.g.token_body = oauth2helper.validate(
                    flask.g.token, identity_provider_url
                )
            except jwt.PyJWTError as e:
                raise werkzeug.exceptions.Unauthorized(description=str(e)) from e
            return func(*func_args, **func_kwargs)

        return wrapper

    return decorator


def _extract_token_body() -> dict:
    if getattr(flask.g, "token_body", None):
        return flask.g.token_body
    try:
        json_header, json_body = oauth2helper.decode(_get_token(flask.request.headers))
        return json_body
    except jwt.PyJWTError:
        return {}


class UserIdFilter(logging.Filter):
    """
    This is a logging filter that makes the user identifier available for use in the logging format.
    Note that we are checking if we are in a request context, as we may want to log things before Flask is fully loaded.
    """

    def __init__(self, token_field_name: str, name: str = ""):
        logging.Filter.__init__(self, name=name)
        self.token_field_name = token_field_name

    def filter(self, record):
        record.user_id = (
            _extract_token_body().get(self.token_field_name, "")
            if flask.has_request_context()
            else ""
        )
        return True
