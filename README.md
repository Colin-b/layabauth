<h2 align="center">Handle OAuth2 authentication for REST APIs</h2>

<p align="center">
<a href="https://pypi.org/project/layabauth/"><img alt="pypi version" src="https://img.shields.io/pypi/v/layabauth"></a>
<a href="https://github.com/Colin-b/layabauth/actions"><img alt="Build status" src="https://github.com/Colin-b/layabauth/workflows/Release/badge.svg"></a>
<a href="https://github.com/Colin-b/layabauth/actions"><img alt="Coverage" src="https://img.shields.io/badge/coverage-100%25-brightgreen"></a>
<a href="https://github.com/psf/black"><img alt="Code style: black" src="https://img.shields.io/badge/code%20style-black-000000.svg"></a>
<a href="https://github.com/Colin-b/layabauth/actions"><img alt="Number of tests" src="https://img.shields.io/badge/tests-50 passed-blue"></a>
<a href="https://pypi.org/project/layabauth/"><img alt="Number of downloads" src="https://img.shields.io/pypi/dm/layabauth"></a>
</p>

As expected by the HTTP specification, token is extracted from `Authorization` header and must be prefixed with `Bearer `.

Token will then be validated and in case it is valid, you will be able to access the raw token (as string) and the decoded token body (as dictionary).

## Starlette

Provides a [Starlette authentication backend](https://www.starlette.io/authentication/): `layabauth.starlette.OAuth2IdTokenBackend`.

3 arguments are required:
* The [JWKs](https://tools.ietf.org/html/rfc7517) URI as defined in .well-known.
 - Azure Active Directory: `https://sts.windows.net/common/discovery/keys`
 - Microsoft Identity Platform: `https://sts.windows.net/common/discovery/keys`
* A callable to create the [authenticated user](https://www.starlette.io/authentication/#users) based on received token.
* A callable to returns [authenticated user scopes](https://www.starlette.io/authentication/#permissions) based on received token.

Below is a sample `Starlette` application with an endpoint requesting a Microsoft issued OAuth2 token.

```python
import starlette.applications
from starlette.authentication import SimpleUser, requires
from starlette.middleware import Middleware
from starlette.middleware.authentication import AuthenticationMiddleware
from starlette.responses import PlainTextResponse

import layabauth.starlette

backend = layabauth.starlette.OAuth2IdTokenBackend(
    jwks_uri="https://sts.windows.net/common/discovery/keys",
    create_user=lambda token, token_body: SimpleUser(token_body["name"]),
    scopes=lambda token, token_body: token_body["scopes"]
)
app = starlette.applications.Starlette(middleware=[Middleware(AuthenticationMiddleware, backend=backend)])

@app.route("/my_endpoint")
@requires('my_scope')
async def my_endpoint(request):
    return PlainTextResponse(request.user.display_name)
```

## Flask

Provides a decorator `layabauth.flask.requires_authentication` to ensure that, in a context of a `Flask` application, a valid OAuth2 token was received.

The [JWKs](https://tools.ietf.org/html/rfc7517) URI as defined in .well-known is the only required argument.
- Azure Active Directory: `https://sts.windows.net/common/discovery/keys`
- Microsoft Identity Platform: `https://sts.windows.net/common/discovery/keys`

If validation fails, an `werkzeug.exceptions.Unauthorized` exception is raised.
Otherwise token is stored in `flask.g.token` and decoded token body is stored in `flask.g.token_body`.

Decorator works fine on `flask-restplus` methods as well.

Below is a sample `Flask` application with an endpoint requesting a Microsoft issued OAuth2 token.

```python
import flask
import layabauth.flask

app = flask.Flask(__name__)

@app.route("/my_endpoint")
@layabauth.flask.requires_authentication("https://sts.windows.net/common/discovery/keys")
def my_endpoint():
    # Optional, ensure that the appropriates scopes are provided
    layabauth.flask.requires_scopes(lambda token, token_body: token_body["scopes"], "my_scope")
    # Return the content of the name entry within the decoded token body.
    return flask.Response(flask.g.token_body["name"])

app.run()
```

## OpenAPI

You can generate OpenAPI 2.0 `security` definition thanks to `layabauth.authorizations`.

You can generate OpenAPI 2.0 `method security` thanks to `layabauth.method_authorizations`

## Testing

Authentication can be mocked using `layabauth.testing.auth_mock` `pytest` fixture.

`token_body` `pytest` fixture returning the decoded token body used in tests must be provided.
`jwks_uri` `pytest` fixture returning the jwks_uri used in tests must be provided.

```python
from layabauth.testing import *


@pytest.fixture
def jwks_uri():
    return "https://sts.windows.net/common/discovery/keys"


@pytest.fixture
def token_body():
    return {"name": "TEST@email.com", "scopes": ["my_scope"]}


def test_authentication(auth_mock, client):
    response = client.get("/my_endpoint", headers={"Authentication": "Bearer mocked_token"})
    assert response.text == "TEST@email.com"
```

## How to install
1. [python 3.7+](https://www.python.org/downloads/) must be installed
2. Use pip to install module:
```sh
python -m pip install layabauth
```
