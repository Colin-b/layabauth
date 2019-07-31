from typing import List
import os.path
import importlib

import flask
import flask_restplus
import flask_cors
import flask_compress
import werkzeug

from pycommon_server import get_environment


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


class _PycommonApi(flask_restplus.Api):
    @werkzeug.cached_property
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
) -> (flask.Flask, flask_restplus.Api):
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
    application = flask.Flask(service_package)

    if cors:
        flask_cors.CORS(application)

    if compress_mimetypes:
        compress = flask_compress.Compress()
        compress.init_app(application)
        application.config["COMPRESS_MIMETYPES"] = compress_mimetypes

    if reverse_proxy:
        application.wsgi_app = _ReverseProxied(application.wsgi_app)

    version = importlib.import_module(f"{service_package}.version").__version__

    return application, _PycommonApi(application, version=version, **kwargs)
