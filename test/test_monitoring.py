import pytest
from flask import Flask
from flask_restplus import Api

import pycommon_server


@pytest.fixture
def app():
    application = Flask(__name__)
    application.testing = True
    api = Api(application, version="3.2.1")

    def pass_details():
        return "pass", {"toto2": {"status": "pass"}}

    pycommon_server.add_monitoring_namespace(api, pass_details)

    return application


def test_health_check_response_on_pass(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json == {
        "details": {"toto2": {"status": "pass"}},
        "releaseId": "3.2.1",
        "status": "pass",
        "version": "3",
    }


def test_generated_swagger(client):
    response = client.get("/swagger.json")
    assert response.status_code == 200
    assert response.json == {
        "swagger": "2.0",
        "basePath": "/",
        "paths": {
            "/changelog": {
                "get": {
                    "responses": {
                        "200": {
                            "description": "Service changelog.",
                            "schema": {
                                "type": "array",
                                "items": {
                                    "$ref": "#/definitions/ChangelogReleaseModel"
                                },
                            },
                        },
                        "500": {
                            "description": "Unable to retrieve changelog.",
                            "schema": {"type": "string"},
                        },
                    },
                    "summary": "Retrieve service changelog",
                    "operationId": "get_changelog",
                    "tags": ["Monitoring"],
                }
            },
            "/health": {
                "get": {
                    "responses": {
                        "200": {
                            "description": "Server is in a coherent state.",
                            "schema": {"$ref": "#/definitions/HealthPass"},
                        },
                        "429": {
                            "description": "Server is almost in a coherent state.",
                            "schema": {"$ref": "#/definitions/HealthWarn"},
                        },
                        "400": {
                            "description": "Server is not in a coherent state.",
                            "schema": {"$ref": "#/definitions/HealthFail"},
                        },
                    },
                    "summary": "Check service health",
                    "description": "This endpoint perform a quick server state check.",
                    "operationId": "get_health",
                    "tags": ["Monitoring"],
                }
            },
        },
        "info": {"title": "API", "version": "3.2.1"},
        "produces": ["application/json"],
        "consumes": ["application/json"],
        "tags": [{"name": "Monitoring", "description": "Monitoring operations"}],
        "definitions": {
            "HealthPass": {
                "required": ["details", "releaseId", "status", "version"],
                "properties": {
                    "status": {
                        "type": "string",
                        "description": "Indicates whether the service status is acceptable or not.",
                        "example": "pass",
                        "enum": ["pass"],
                    },
                    "version": {
                        "type": "string",
                        "description": "Public version of the service.",
                        "example": "1",
                    },
                    "releaseId": {
                        "type": "string",
                        "description": "Version of the service.",
                        "example": "1.0.0",
                    },
                    "details": {
                        "type": "object",
                        "description": "Provides more details about the status of the service.",
                    },
                },
                "type": "object",
            },
            "HealthWarn": {
                "required": ["details", "releaseId", "status", "version"],
                "properties": {
                    "status": {
                        "type": "string",
                        "description": "Indicates whether the service status is acceptable or not.",
                        "example": "warn",
                        "enum": ["warn"],
                    },
                    "version": {
                        "type": "string",
                        "description": "Public version of the service.",
                        "example": "1",
                    },
                    "releaseId": {
                        "type": "string",
                        "description": "Version of the service.",
                        "example": "1.0.0",
                    },
                    "details": {
                        "type": "object",
                        "description": "Provides more details about the status of the service.",
                    },
                },
                "type": "object",
            },
            "HealthFail": {
                "required": ["details", "releaseId", "status", "version"],
                "properties": {
                    "status": {
                        "type": "string",
                        "description": "Indicates whether the service status is acceptable or not.",
                        "example": "fail",
                        "enum": ["fail"],
                    },
                    "version": {
                        "type": "string",
                        "description": "Public version of the service.",
                        "example": "1",
                    },
                    "releaseId": {
                        "type": "string",
                        "description": "Version of the service.",
                        "example": "1.0.0",
                    },
                    "details": {
                        "type": "object",
                        "description": "Provides more details about the status of the service.",
                    },
                    "output": {"type": "string", "description": "Raw error output."},
                },
                "type": "object",
            },
            "ChangelogReleaseModel": {
                "required": ["release_date", "version"],
                "properties": {
                    "version": {
                        "type": "string",
                        "description": "Release version following semantic versioning.",
                        "example": "3.12.5",
                    },
                    "release_date": {
                        "type": "string",
                        "format": "date",
                        "description": "Release date.",
                        "example": "2019-12-31",
                    },
                    "added": {
                        "type": "array",
                        "items": {"type": "string", "description": "New features."},
                    },
                    "changed": {
                        "type": "array",
                        "items": {
                            "type": "string",
                            "description": "Changes in existing functionaliy.",
                        },
                    },
                    "deprecated": {
                        "type": "array",
                        "items": {
                            "type": "string",
                            "description": "Soon-to-be removed features.",
                        },
                    },
                    "removed": {
                        "type": "array",
                        "items": {"type": "string", "description": "Removed features."},
                    },
                    "fixed": {
                        "type": "array",
                        "items": {"type": "string", "description": "Any bug fixes."},
                    },
                    "security": {
                        "type": "array",
                        "items": {"type": "string", "description": "Vulnerabilities."},
                    },
                },
                "type": "object",
            },
        },
        "responses": {
            "ParseError": {"description": "When a mask can't be parsed"},
            "MaskError": {"description": "When any error occurs on mask"},
        },
    }
