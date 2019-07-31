import re
from typing import List, Optional
import os.path
import inspect
import json
import time
import sys
import traceback
import logging
import functools
from collections import OrderedDict

import flask
import flask_restplus


logger = logging.getLogger(__name__)


def add_monitoring_namespace(
    api: flask_restplus.Api, health_details: callable
) -> flask_restplus.Namespace:
    """
    Create a monitoring namespace containing:
     * Health check endpoint implementing https://inadarei.github.io/rfc-healthcheck/
     * Changelog endpoint parsing https://keepachangelog.com/en/1.0.0/

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
        release_pattern = re.compile("^## \[(.*)\] - (.*)$")
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
                elif "### Added" == line:
                    current_category = current_release.setdefault("added", [])
                elif "### Changed" == line:
                    current_category = current_release.setdefault("changed", [])
                elif "### Deprecated" == line:
                    current_category = current_release.setdefault("deprecated", [])
                elif "### Removed" == line:
                    current_category = current_release.setdefault("removed", [])
                elif "### Fixed" == line:
                    current_category = current_release.setdefault("fixed", [])
                elif "### Security" == line:
                    current_category = current_release.setdefault("security", [])
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
                        "status": flask_restplus.fields.String(
                            description="Indicates whether the service status is acceptable or not.",
                            required=True,
                            example="pass",
                            enum=["pass"],
                        ),
                        "version": flask_restplus.fields.String(
                            description="Public version of the service.",
                            required=True,
                            example="1",
                        ),
                        "releaseId": flask_restplus.fields.String(
                            description="Version of the service.",
                            required=True,
                            example="1.0.0",
                        ),
                        "details": flask_restplus.fields.Raw(
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
                        "status": flask_restplus.fields.String(
                            description="Indicates whether the service status is acceptable or not.",
                            required=True,
                            example="warn",
                            enum=["warn"],
                        ),
                        "version": flask_restplus.fields.String(
                            description="Public version of the service.",
                            required=True,
                            example="1",
                        ),
                        "releaseId": flask_restplus.fields.String(
                            description="Version of the service.",
                            required=True,
                            example="1.0.0",
                        ),
                        "details": flask_restplus.fields.Raw(
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
                        "status": flask_restplus.fields.String(
                            description="Indicates whether the service status is acceptable or not.",
                            required=True,
                            example="fail",
                            enum=["fail"],
                        ),
                        "version": flask_restplus.fields.String(
                            description="Public version of the service.",
                            required=True,
                            example="1",
                        ),
                        "releaseId": flask_restplus.fields.String(
                            description="Version of the service.",
                            required=True,
                            example="1.0.0",
                        ),
                        "details": flask_restplus.fields.Raw(
                            description="Provides more details about the status of the service.",
                            required=True,
                        ),
                        "output": flask_restplus.fields.String(
                            description="Raw error output.", required=False
                        ),
                    },
                ),
            ),
        }
    )
    class Health(flask_restplus.Resource):
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
            response = flask.make_response(json.dumps(body), code)
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
                            "version": flask_restplus.fields.String(
                                description="Release version following semantic versioning.",
                                required=True,
                                example="3.12.5",
                            ),
                            "release_date": flask_restplus.fields.Date(
                                description="Release date.",
                                required=True,
                                example="2019-12-31",
                            ),
                            "added": flask_restplus.fields.List(
                                flask_restplus.fields.String(
                                    description="New features."
                                )
                            ),
                            "changed": flask_restplus.fields.List(
                                flask_restplus.fields.String(
                                    description="Changes in existing functionaliy."
                                )
                            ),
                            "deprecated": flask_restplus.fields.List(
                                flask_restplus.fields.String(
                                    description="Soon-to-be removed features."
                                )
                            ),
                            "removed": flask_restplus.fields.List(
                                flask_restplus.fields.String(
                                    description="Removed features."
                                )
                            ),
                            "fixed": flask_restplus.fields.List(
                                flask_restplus.fields.String(
                                    description="Any bug fixes."
                                )
                            ),
                            "security": flask_restplus.fields.List(
                                flask_restplus.fields.String(
                                    description="Vulnerabilities."
                                )
                            ),
                        },
                    )
                ],
            ),
            500: ("Unable to retrieve changelog.", flask_restplus.fields.String()),
        }
    )
    class Changelog(flask_restplus.Resource):
        def get(self):
            """
            Retrieve service changelog.
            """
            if changelog is not None:
                return flask.jsonify(changelog)
            return flask.make_response(
                "No changelog can be found. Please contact support.", 500
            )

    return namespace


class _Statistics:
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
        if flask.has_request_context():
            self.stats.update(
                {
                    # TODO Explain why the key name should change if v length is not 1
                    f"request_args.{k}"
                    if len(v) == 1
                    else k: v[0]
                    if len(v) == 1
                    else v
                    for k, v in dict(flask.request.args).items()
                }
            )
            self.stats.update(
                {
                    f"request_headers.{k}": v
                    for k, v in dict(flask.request.headers).items()
                }
            )
        self.start = time.perf_counter()

    def success(self):
        self.stats["request_processing_time"] = time.perf_counter() - self.start
        logger.info(self.stats)

    def exception_occurred(self):
        if flask.has_request_context():
            self.stats["request.data"] = flask.request.data
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
    @functools.wraps(func)
    def wrapper(*func_args, **func_kwargs):
        if "Health.get" in func.__qualname__:
            return func(*func_args, **func_kwargs)

        statistics = _Statistics(func, *func_args, **func_kwargs)
        try:
            ret = func(*func_args, **func_kwargs)
            statistics.success()
            return ret
        except Exception:
            statistics.exception_occurred()
            raise

    return wrapper


flask_restplus.Resource.method_decorators.append(_log_request_details)
