import logging
import functools
import json

import flask
import httpx
import werkzeug
from jose import exceptions, jws

from layabauth import _http


def requires_authentication(jwks_uri: str, **httpx_kwargs):
    """
    Ensure that a valid JWT is received before entering the annotated endpoint.

    :param jwks_uri: The JWKs URI as defined in .well-known.
    For more information on JWK, refer to https://tools.ietf.org/html/rfc7517
        * Azure Active Directory: https://sts.windows.net/common/discovery/keys
        * Microsoft Identity Platform: https://sts.windows.net/common/discovery/keys
    :param httpx_kwargs: Any other argument will be provided to httpx.Client to be able to retrieve the keys.
    """

    def decorator(func):
        @functools.wraps(func)
        def wrapper(*func_args, **func_kwargs):
            try:
                flask.g.token = _http._get_token(flask.request.headers)
                if not flask.g.token:
                    raise werkzeug.exceptions.Unauthorized()
                with httpx.Client(**httpx_kwargs) as client:
                    key = _http.keys(client, jwks_uri)
                flask.g.token_body = _http.validate(flask.g.token, key)
            except exceptions.JOSEError as e:
                raise werkzeug.exceptions.Unauthorized(description=str(e)) from e
            return func(*func_args, **func_kwargs)

        return wrapper

    return decorator


def requires_scopes(scopes: callable, *expected_scopes: str):
    """
    Ensure that the token contains the required scopes.
    Raises werkzeug.exceptions.Forbidden otherwise.

    :param scopes: callable receiving the token and the decoded token body and returning the list of associated scopes str.
    :param expected_scopes: all expected scopes in the token.
    """
    try:
        scopes = scopes(token=flask.g.token, token_body=flask.g.token_body) or []
    except:
        scopes = []

    for expected_scope in expected_scopes:
        if expected_scope not in scopes:
            raise werkzeug.exceptions.Forbidden(
                description=f"The {expected_scope} must be provided in the token."
            )


def _extract_token_body() -> dict:
    if getattr(flask.g, "token_body", None):
        return flask.g.token_body

    token = _http._get_token(flask.request.headers)
    if not token:
        return {}

    try:
        return json.loads(jws.get_unverified_claims(token=token))
    except exceptions.JOSEError:
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
