import logging
import uuid

import flask


def _request_id():
    """
    Returns the current request identifier or a new one if there is none
    Also store it in flask.g.request_id

    In order of preference:
    * If we have already created a request identifier and stored it in the flask.g context local, use that
    * If a client has passed in the X-Request-Id header, create a new ID with that prepended
    * Otherwise, generate a request identifier and store it in flask.g.request_id

    :return: current request identifier or a new one if there is none
    """
    if getattr(flask.g, "request_id", None):
        return flask.g.request_id

    headers = flask.request.headers
    original_request_id = headers.get("X-Request-Id")
    request_id = (
        f"{original_request_id},{uuid.uuid4()}" if original_request_id else uuid.uuid4()
    )

    flask.g.request_id = request_id
    return request_id


class RequestIdFilter(logging.Filter):
    """
    This is a logging filter that makes the request identifier available for use in the logging format.
    This filter support lookup in flask context for the request id
    Note that we are checking if we are in a request context, as we may want to log things before Flask is fully loaded.
    """

    def filter(self, record):
        record.request_id = _request_id() if flask.has_request_context() else ""
        return True
