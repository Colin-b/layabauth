<h2 align="center">Authentication for layab</h2>

<p align="center">
<a href="https://pypi.org/project/layabauth/"><img alt="pypi version" src="https://img.shields.io/pypi/v/layabauth"></a>
<a href="https://travis-ci.org/Colin-b/layabauth"><img alt="Build status" src="https://api.travis-ci.org/Colin-b/layabauth.svg?branch=develop"></a>
<a href="https://travis-ci.org/Colin-b/layabauth"><img alt="Coverage" src="https://img.shields.io/badge/coverage-100%25-brightgreen"></a>
<a href="https://github.com/psf/black"><img alt="Code style: black" src="https://img.shields.io/badge/code%20style-black-000000.svg"></a>
<a href="https://travis-ci.org/Colin-b/layabauth"><img alt="Number of tests" src="https://img.shields.io/badge/tests-20 passed-blue"></a>
<a href="https://pypi.org/project/layabauth/"><img alt="Number of downloads" src="https://img.shields.io/pypi/dm/layabauth"></a>
</p>

Provides a decorator to ensure that, in a context of a `Flask` server, a valid OAuth2 token was received.

As expected by the HTTP specification, token is extracted from `Authorization` header and must be prefixed with `Bearer `.

If validation fails, an `werkzeug.exceptions.Unauthorized` exception is raised.
Otherwise user details are stored in `flask.g.current_user`, this variable is an instance of the `User` class, 
it contains `name` property holding the authenticated user name (extracted from the upn field inside the token).

Decorator works fine on `flask-restplus` methods as well.

Below is a sample `Flask` application with an endpoint requesting a Microsoft issued OAuth2 token.

```python
import flask
import layabauth

app = flask.Flask(__name__)

@app.route("/my_endpoint")
@layabauth.requires_authentication("https://sts.windows.net/common/discovery/keys")
def my_endpoint():
    return "OK"

app.run()
```

## OpenAPI

You can generate OpenAPI `security` definition thanks to `layabauth.authorizations`.

You can generate OpenAPI `method security` thanks to `layabauth.method_authorizations`

## Testing

Authentication can be mocked using `layabauth.testing.auth_mock` `pytest` fixture.

`upn` `pytest` fixture returning the UPN located in token used in tests must be provided.

```python
from layabauth.testing import *

@pytest.fixture
def upn():
    return "TEST@email.com"


def test_authentication(auth_mock):
    pass
```

## How to install
1. [python 3.6+](https://www.python.org/downloads/) must be installed
2. Use pip to install module:
```sh
python -m pip install layabauth
```
