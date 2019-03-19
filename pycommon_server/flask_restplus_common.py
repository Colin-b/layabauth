import importlib
import inspect
import json
import logging
import os
import sys
import re
import time
import traceback
from collections import OrderedDict
from functools import wraps
from http import HTTPStatus
from typing import List, Dict, Union, Optional
from urllib.parse import urlparse

import flask
from flask import request, has_request_context, make_response, Flask, jsonify
from flask_compress import Compress
from flask_cors import CORS
from flask_restplus import Resource, fields, Api, Namespace
from werkzeug import cached_property
from werkzeug.exceptions import Unauthorized

from pycommon_server.configuration import get_environment

logger = logging.getLogger(__name__)


def add_monitoring_namespace(api: Api, health_details: callable) -> Namespace:
    """
    Create a monitoring namespace containing:
     * Health check endpoint implementing https://inadarei.github.io/rfc-healthcheck/
     * Changelog endpoint

    :param api: The root Api
    :param health_details: Function returning a tuple with a string providing the status (pass, warn, fail)
    and the details
    :return: The monitoring namespace (you can use it to add additional endpoints)
    """
    namespace = api.namespace(
        "Monitoring", path="/", description="Monitoring operations"
    )
    version = api.version.split(".", maxsplit=1)[0]
    release_id = api.version

    def _markdown_to_dict(changelog_path: str) -> List[dict]:
        changes = []
        current_release = {}
        current_category = None
        release_pattern = re.compile("^## Version (.*) \((.*)\) ##$")
        with open(changelog_path) as change_log:
            for line in change_log:
                line = line.strip(" \n")
                release = release_pattern.fullmatch(line)
                if release:
                    current_release = {
                        "version": release.group(1),
                        "release_date": release.group(2),
                    }
                    changes.append(current_release)
                elif "### Release notes ###" == line:
                    current_category = current_release.setdefault("release_notes", [])
                elif "### Enhancements ###" == line:
                    current_category = current_release.setdefault("enhancements", [])
                elif "### Bug fixes ###" == line:
                    current_category = current_release.setdefault("bug_fixes", [])
                elif "### Known issues ###" == line:
                    current_category = current_release.setdefault("known_issues", [])
                elif line and current_category is not None:
                    current_category.append(line)
        return changes

    def _retrieve_changelog() -> Optional[List[dict]]:
        try:
            server_py_python_path = inspect.stack()[2][0]
            server_py_module = inspect.getmodule(server_py_python_path)
            server_py_file_path = server_py_module.__file__
            changelog_path = os.path.join(
                os.path.abspath(os.path.dirname(server_py_file_path)),
                "..",
                "CHANGELOG.md",
            )
            return _markdown_to_dict(changelog_path)
        except:
            return

    changelog = _retrieve_changelog()

    @namespace.route("/health")
    @namespace.doc(
        responses={
            200: (
                "Server is in a coherent state.",
                namespace.model(
                    "HealthPass",
                    {
                        "status": fields.String(
                            description="Indicates whether the service status is acceptable or not.",
                            required=True,
                            example="pass",
                            enum=["pass"],
                        ),
                        "version": fields.String(
                            description="Public version of the service.",
                            required=True,
                            example="1",
                        ),
                        "releaseId": fields.String(
                            description="Version of the service.",
                            required=True,
                            example="1.0.0",
                        ),
                        "details": fields.Raw(
                            description="Provides more details about the status of the service.",
                            required=True,
                        ),
                    },
                ),
            ),
            429: (
                "Server is almost in a coherent state.",
                namespace.model(
                    "HealthWarn",
                    {
                        "status": fields.String(
                            description="Indicates whether the service status is acceptable or not.",
                            required=True,
                            example="warn",
                            enum=["warn"],
                        ),
                        "version": fields.String(
                            description="Public version of the service.",
                            required=True,
                            example="1",
                        ),
                        "releaseId": fields.String(
                            description="Version of the service.",
                            required=True,
                            example="1.0.0",
                        ),
                        "details": fields.Raw(
                            description="Provides more details about the status of the service.",
                            required=True,
                        ),
                    },
                ),
            ),
            400: (
                "Server is not in a coherent state.",
                namespace.model(
                    "HealthFail",
                    {
                        "status": fields.String(
                            description="Indicates whether the service status is acceptable or not.",
                            required=True,
                            example="fail",
                            enum=["fail"],
                        ),
                        "version": fields.String(
                            description="Public version of the service.",
                            required=True,
                            example="1",
                        ),
                        "releaseId": fields.String(
                            description="Version of the service.",
                            required=True,
                            example="1.0.0",
                        ),
                        "details": fields.Raw(
                            description="Provides more details about the status of the service.",
                            required=True,
                        ),
                        "output": fields.String(
                            description="Raw error output.", required=False
                        ),
                    },
                ),
            ),
        }
    )
    class Health(Resource):
        def get(self):
            """
            Check service health.
            This endpoint perform a quick server state check.
            """
            try:
                status, details = health_details()
                return self._send_status(status, details)
            except Exception as e:
                return self._send_status("fail", {}, output=str(e))

        @staticmethod
        def _send_status(status: str, details: dict, **kwargs):
            body = {
                "status": status,
                "version": version,
                "releaseId": release_id,
                "details": details,
            }
            body.update(kwargs)
            code = 200  # Consul consider every 2** as Ok
            if "fail" == status:
                code = 400  # Consul consider every non 429 or 2** as Critical
            elif "warn" == status:
                code = 429  # Consul consider a 429 as a Warning
            response = make_response(json.dumps(body), code)
            response.headers["Content-Type"] = "application/health+json"
            return response

    @namespace.route("/changelog")
    @namespace.doc(
        responses={
            200: (
                "Service changelog.",
                [
                    namespace.model(
                        "ChangelogReleaseModel",
                        {
                            "version": fields.String(
                                description="Release version formatted as major.minor.patch where major, minor and patch are numbers.",
                                required=True,
                                example="3.12.5",
                            ),
                            "release_date": fields.Date(
                                description="Release date.",
                                required=True,
                                example="2019-12-31",
                            ),
                            "release_notes": fields.List(
                                fields.String(
                                    description="Release note.",
                                    example="Foo will now reject bar.",
                                )
                            ),
                            "enhancements": fields.List(
                                fields.String(
                                    description="Enhancement.",
                                    example="Foo can now return bar.",
                                )
                            ),
                            "bug_fixes": fields.List(
                                fields.String(
                                    description="Bug fix.",
                                    example="Foo is now properly returning bar.",
                                )
                            ),
                            "known_issues": fields.List(
                                fields.String(
                                    description="Known issue with this release.",
                                    example="Foo does not return bar yet.",
                                )
                            ),
                        },
                    )
                ],
            ),
            500: ("Unable to retrieve changelog.", fields.String()),
        }
    )
    class Changelog(Resource):
        def get(self):
            """
            Retrieve service changelog.
            """
            if changelog is not None:
                return jsonify(changelog)
            return make_response(
                "No changelog can be found. Please contact support.", 500
            )

    return namespace


def base_path() -> str:
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
    response = make_response(json.dumps({"status": "Successful"}), HTTPStatus.CREATED)
    response.headers["Content-Type"] = "application/json"
    response.headers["location"] = f"{base_path()}{url}"
    return response


def created_response_doc(api: Union[Api, Namespace]) -> Dict[str, dict]:
    return {
        "responses": {
            HTTPStatus.CREATED.value: (
                "Created",
                api.model("Created", {"status": fields.String(default="Successful")}),
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
    response = make_response(json.dumps({"status": "Successful"}), HTTPStatus.CREATED)
    response.headers["Content-Type"] = "application/json"
    response.headers["location"] = f"{base_path()}{url}"
    return response


def updated_response_doc(api: Union[Api, Namespace]) -> Dict[str, dict]:
    return {
        "responses": {
            HTTPStatus.CREATED.value: (
                "Updated",
                api.model("Updated", {"status": fields.String(default="Successful")}),
                {"headers": {"location": "Location of updated resource."}},
            )
        }
    }


deleted_response = "", HTTPStatus.NO_CONTENT
deleted_response_doc = HTTPStatus.NO_CONTENT, "Deleted"


class User:
    def __init__(self, decoded_body: dict):
        import oauth2helper.content

        self.name = oauth2helper.content.user_name(decoded_body)


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
            from jwt.exceptions import InvalidTokenError, InvalidKeyError
            import oauth2helper.token

            json_header, json_body = oauth2helper.token.validate(token)
            return User(json_body)
        except ImportError:
            raise Unauthorized(
                "Server is missing oauth2helper module to handle authentication."
            )
        except (InvalidTokenError or InvalidKeyError) as e:
            raise Unauthorized(e.args[0])


def requires_authentication(func):
    @wraps(func)
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


class Statistics:
    def __init__(self, func, *func_args, **func_kwargs):
        args_name = list(
            OrderedDict.fromkeys(
                inspect.getfullargspec(func)[0] + list(func_kwargs.keys())
            )
        )
        args_dict = OrderedDict(
            list(zip(args_name, func_args)) + list(func_kwargs.items())
        )
        self.stats = {"func_name": ".".join(func.__qualname__.rsplit(".", 2)[-2:])}
        self.stats.update(args_dict)
        # add request args
        if has_request_context():
            self.stats.update(
                {
                    # TODO Explain why the key name should change if v length is not 1
                    f"request_args.{k}"
                    if len(v) == 1
                    else k: v[0]
                    if len(v) == 1
                    else v
                    for k, v in dict(request.args).items()
                }
            )
            self.stats.update(
                {f"request_headers.{k}": v for k, v in dict(request.headers).items()}
            )
        self.start = time.perf_counter()

    def success(self):
        self.stats["request_processing_time"] = time.perf_counter() - self.start
        logger.info(self.stats)

    def exception_occurred(self):
        if has_request_context():
            self.stats["request.data"] = request.data
        exc_type, exc_value, exc_traceback = sys.exc_info()
        trace = traceback.extract_tb(exc_traceback)
        # Do not want the current frame in the traceback
        if len(trace) > 1:
            trace = trace[1:]
        trace.reverse()
        trace_summary = "/".join(
            [
                os.path.splitext(os.path.basename(tr.filename))[0] + "." + tr.name
                for tr in trace
            ]
        )
        self.stats.update(
            {
                "error.summary": trace_summary,
                "error.class": exc_type.__name__,
                "error.msg": str(exc_value),
                "error.traceback": traceback.format_exc(),
            }
        )
        logger.critical(self.stats)


def _log_request_details(func):
    @wraps(func)
    def wrapper(*func_args, **func_kwargs):
        if "Health.get" in func.__qualname__:
            return func(*func_args, **func_kwargs)

        statistics = Statistics(func, *func_args, **func_kwargs)
        try:
            ret = func(*func_args, **func_kwargs)
            statistics.success()
            return ret
        except Exception:
            statistics.exception_occurred()
            raise

    return wrapper


class _ReverseProxied:
    """
    Wrap the application in this middleware and configure the
    front-end server to add these headers, to let you quietly bind
    this to a URL other than / and to an HTTP scheme that is
    different than what is used locally.

    :param app: the WSGI application
    """

    def __init__(self, app):
        self.app = app

    def __call__(self, environ, start_response):
        original_url = environ.get("HTTP_X_ORIGINAL_REQUEST_URI", "")
        if original_url:
            script_name = "/" + original_url.split("/", maxsplit=2)[1]
            environ["SCRIPT_NAME"] = script_name

            path_info = environ.get("PATH_INFO", "")
            if path_info.startswith(script_name):
                environ["PATH_INFO"] = path_info[len(script_name) :]

            scheme = environ.get("HTTP_X_SCHEME", "")
            if scheme:
                environ["wsgi.url_scheme"] = scheme
        return self.app(environ, start_response)


class PycommonApi(Api):
    @cached_property
    def __schema__(self):
        schema = super().__schema__
        schema["info"]["x-server-environment"] = get_environment()
        return schema


def create_api(
    file_path: str,
    cors: bool = True,
    compress_mimetypes: List[str] = None,
    reverse_proxy: bool = True,
    **kwargs,
) -> (Flask, Api):
    """
    Create Flask application and related Flask-RestPlus API instance.

    :param file_path: server.py __file__ variable.
    :param cors: If CORS (Cross Resource) should be enabled. Activated by default.
    :param compress_mimetypes: List of mime-types that should be compressed. No compression by default.
    :param reverse_proxy: If server should handle reverse-proxy configuration. Enabled by default.
    :param kwargs: Additional Flask-RestPlus API arguments.
    :return: A tuple with 2 elements: Flask application, Flask-RestPlus API
    """
    service_package = os.path.basename(os.path.dirname(file_path))
    application = Flask(service_package)

    if cors:
        CORS(application)

    if compress_mimetypes:
        compress = Compress()
        compress.init_app(application)
        application.config["COMPRESS_MIMETYPES"] = compress_mimetypes

    if reverse_proxy:
        application.wsgi_app = _ReverseProxied(application.wsgi_app)

    version = importlib.import_module(f"{service_package}._version").__version__

    return application, PycommonApi(application, version=version, **kwargs)


Resource.method_decorators.append(_log_request_details)
