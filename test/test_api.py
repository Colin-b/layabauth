import gzip
import json

import flask
import flask_restplus

import pycommon_server


def test_basic_api():
    app, api = pycommon_server.create_api(
        __file__,
        title="TestApi",
        description="Testing API",
        cors=False,
        reverse_proxy=False,
    )

    with app.test_client() as client:
        response = client.get("/swagger.json")
        assert response.status_code == 200
        assert response.json == {
            "swagger": "2.0",
            "basePath": "/",
            "paths": {},
            "info": {
                "title": "TestApi",
                "version": "1.0.0",
                "description": "Testing API",
                "x-server-environment": "default",
            },
            "produces": ["application/json"],
            "consumes": ["application/json"],
            "tags": [],
            "responses": {
                "ParseError": {"description": "When a mask can't be parsed"},
                "MaskError": {"description": "When any error occurs on mask"},
            },
        }


def test_cors_api():
    app, api = pycommon_server.create_api(
        __file__, title="TestApi", description="Testing API", reverse_proxy=False
    )

    with app.test_client() as client:
        response = client.get("/swagger.json")
        assert response.status_code == 200
        assert response.json == {
            "swagger": "2.0",
            "basePath": "/",
            "paths": {},
            "info": {
                "title": "TestApi",
                "version": "1.0.0",
                "description": "Testing API",
                "x-server-environment": "default",
            },
            "produces": ["application/json"],
            "consumes": ["application/json"],
            "tags": [],
            "responses": {
                "ParseError": {"description": "When a mask can't be parsed"},
                "MaskError": {"description": "When any error occurs on mask"},
            },
        }
        assert response.headers.get("Access-Control-Allow-Origin") == "*"


def test_compress_api():
    app, api = pycommon_server.create_api(
        __file__,
        title="TestApi",
        description="Testing API",
        cors=False,
        reverse_proxy=False,
        compress_mimetypes=["application/json"],
    )

    heavy_answer = {"test": 1000 * "A"}

    @api.route("/test")
    class TestRoute(flask_restplus.Resource):
        def get(self):
            return flask.Response(
                response=json.dumps(heavy_answer), mimetype="application/json"
            )

    with app.test_client() as client:
        response = client.get("/test", headers=[("Accept-Encoding", "gzip")])
        assert response.status_code == 200
        assert response.content_encoding == "gzip"
        assert (
            json.loads(gzip.decompress(response.data).decode("utf-8")) == heavy_answer
        )


def test_reverse_proxy_api():
    app, api = pycommon_server.create_api(
        __file__, title="TestApi", description="Testing API", cors=False
    )

    with app.test_client() as client:
        response = client.get(
            "/swagger.json",
            headers=[("X-Original-Request-Uri", "/behind_reverse_proxy")],
        )
        assert response.status_code == 200
        assert response.json == {
            "swagger": "2.0",
            "basePath": "/behind_reverse_proxy",
            "paths": {},
            "info": {
                "title": "TestApi",
                "version": "1.0.0",
                "description": "Testing API",
                "x-server-environment": "default",
            },
            "produces": ["application/json"],
            "consumes": ["application/json"],
            "tags": [],
            "responses": {
                "ParseError": {"description": "When a mask can't be parsed"},
                "MaskError": {"description": "When any error occurs on mask"},
            },
        }


def test_extra_parameters_api():
    app, api = pycommon_server.create_api(
        __file__,
        title="TestApi",
        description="Testing API",
        cors=False,
        reverse_proxy=False,
        license_url="my.license.com",
        license="MIT",
    )

    with app.test_client() as client:
        response = client.get(
            "/swagger.json",
            headers=[("X-Original-Request-Uri", "/behind_reverse_proxy")],
        )
        assert response.status_code == 200
        assert response.json == {
            "swagger": "2.0",
            "basePath": "/",
            "paths": {},
            "info": {
                "title": "TestApi",
                "version": "1.0.0",
                "description": "Testing API",
                "x-server-environment": "default",
                "license": {"name": "MIT", "url": "my.license.com"},
            },
            "produces": ["application/json"],
            "consumes": ["application/json"],
            "tags": [],
            "responses": {
                "ParseError": {"description": "When a mask can't be parsed"},
                "MaskError": {"description": "When any error occurs on mask"},
            },
        }
