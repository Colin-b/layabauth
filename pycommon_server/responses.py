import json
from typing import Union, Dict
import http
from urllib.parse import urlparse

import flask
import flask_restplus


def _base_path() -> str:
    """
    Return service base path (handle the fact that client may be behind a reverse proxy).
    """
    if "X-Original-Request-Uri" in flask.request.headers:
        service_path = (
            "/"
            + flask.request.headers["X-Original-Request-Uri"].split("/", maxsplit=2)[1]
        )
        return f'{flask.request.scheme}://{flask.request.headers["Host"]}{service_path}'
    parsed = urlparse(flask.request.base_url)
    return f"{parsed.scheme}://{parsed.netloc}"


def created_response(url: str) -> flask.Response:
    """
    Create a response to return to the client in case of a successful POST request.

    :param url: Server relative URL returning the created resource(s).
    :return: Response containing the location of the new resource.
    """
    response = flask.make_response(
        json.dumps({"status": "Successful"}), http.HTTPStatus.CREATED
    )
    response.headers["Content-Type"] = "application/json"
    response.headers["location"] = f"{_base_path()}{url}"
    return response


def created_response_doc(
    api: Union[flask_restplus.Api, flask_restplus.Namespace]
) -> Dict[str, dict]:
    return {
        "responses": {
            http.HTTPStatus.CREATED.value: (
                "Created",
                api.model(
                    "Created",
                    {"status": flask_restplus.fields.String(default="Successful")},
                ),
                {"headers": {"location": "Location of created resource."}},
            )
        }
    }


def updated_response(url: str) -> flask.Response:
    """
    Create a response to return to the client in case of a successful PUT request.

    :param url: Server relative URL returning the updated resource(s).
    :return: Response containing the location of the updated resource.
    """
    response = flask.make_response(
        json.dumps({"status": "Successful"}), http.HTTPStatus.CREATED
    )
    response.headers["Content-Type"] = "application/json"
    response.headers["location"] = f"{_base_path()}{url}"
    return response


def updated_response_doc(
    api: Union[flask_restplus.Api, flask_restplus.Namespace]
) -> Dict[str, dict]:
    return {
        "responses": {
            http.HTTPStatus.CREATED.value: (
                "Updated",
                api.model(
                    "Updated",
                    {"status": flask_restplus.fields.String(default="Successful")},
                ),
                {"headers": {"location": "Location of updated resource."}},
            )
        }
    }


deleted_response = "", http.HTTPStatus.NO_CONTENT
deleted_response_doc = http.HTTPStatus.NO_CONTENT, "Deleted"
