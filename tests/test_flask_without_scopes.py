import flask
import flask_restx
import flask.testing

import layabauth.flask
from layabauth.testing import *


@pytest.fixture
def app() -> flask.Flask:
    application = flask.Flask(__name__)
    application.testing = True
    api = flask_restx.Api(application)

    @api.route("/requires_scopes")
    class RequiresScopes(flask_restx.Resource):
        @layabauth.flask.requires_authentication("https://test_identity_provider")
        def get(self):
            layabauth.flask.requires_scopes(
                lambda token, token_body: token_body["scopes"], "scope1", "scope2"
            )
            return flask.g.token_body

    return application


@pytest.fixture
def jwks_uri():
    return "https://test_identity_provider"


@pytest.fixture
def token_body():
    return {"upn": "TEST@email.com"}


def test_auth_mock_without_scopes(client: flask.testing.FlaskClient, auth_mock):
    response = client.open(
        method="GET",
        path="/requires_scopes",
        headers={"Authorization": "Bearer my_token"},
    )
    assert response.status_code == 403
    assert response.json == {"message": "The scope1 must be provided in the token."}
