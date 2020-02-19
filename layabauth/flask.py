import logging
import functools
from typing import Optional

import flask
import werkzeug
import jwt.exceptions
import oauth2helper

from layabauth._authentication import _to_user, _get_token, User


def requires_authentication(identity_provider_url: str):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*func_args, **func_kwargs):
            try:
                flask.g.current_user = _to_user(
                    _get_token(flask.request.headers), identity_provider_url
                )
            except (
                jwt.exceptions.InvalidTokenError or jwt.exceptions.InvalidKeyError
            ) as e:
                raise werkzeug.exceptions.Unauthorized(description=str(e))
            return func(*func_args, **func_kwargs)

        return wrapper

    return decorator


def _extract_user_name() -> Optional[str]:
    if getattr(flask.g, "current_user", None):
        return flask.g.current_user.name
    try:
        json_header, json_body = oauth2helper.decode(_get_token(flask.request.headers))
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
