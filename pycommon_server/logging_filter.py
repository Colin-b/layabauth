import logging
import uuid
import flask
from pycommon_server.jwt_checker import get_user

try:
    from celery import current_task
except Exception as e:
    current_task = None


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


class RequestIdFilter(logging.Filter):
    """
    This is a logging filter that makes the request identifier available for use in the logging format.
    This filter support lookup in flask context for the request id or in a celery context
    Note that we are checking if we are in a request context, as we may want to log things before Flask is fully loaded.
    """

    def filter(self, record):
        record.request_id = (
            _request_id()
            if flask.has_request_context()
            else current_task.request.id
            if current_task
            and hasattr(current_task, "request")
            and hasattr(current_task.request, "id")
            else ""
        )
        return True


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
