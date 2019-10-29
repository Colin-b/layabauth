<h2 align="center">Authentication for layab</h2>

<p align="center">
<a href='https://github.tools.digital.engie.com/gempy/layabauth/releases/latest'><img src='https://pse.tools.digital.engie.com/all/buildStatus/icon?job=team/layabauth/master&config=version'></a>
<a href='https://pse.tools.digital.engie.com/all/job/team/view/Python%20modules/job/layabauth/job/master/'><img src='https://pse.tools.digital.engie.com/all/buildStatus/icon?job=team/layabauth/master'></a>
<a href='https://pse.tools.digital.engie.com/all/job/team/view/Python%20modules/job/layabauth/job/master/cobertura/'><img src='https://pse.tools.digital.engie.com/all/buildStatus/icon?job=team/layabauth/master&config=testCoverage'></a>
<a href="https://github.com/psf/black"><img alt="Code style: black" src="https://img.shields.io/badge/code%20style-black-000000.svg"></a>
<a href='https://pse.tools.digital.engie.com/all/job/team/view/Python%20modules/job/layabauth/job/master/lastSuccessfulBuild/testReport/'><img src='https://pse.tools.digital.engie.com/all/buildStatus/icon?job=team/layabauth/master&config=testCount'></a>
</p>

Provides a decorator to ensure that, in a context of a `Flask` server, a valid OAuth2 token was received.

As expected by the HTTP specification, token is extracted from `Authorization` header and must be prefixed with `Bearer `.

If validation fails, an `werkzeug.exceptions.Unauthorized` exception is raised.
Otherwise user details are stored in `flask.g.current_user`.

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
python -m pip install layabauth -i https://all-team-remote:tBa%40W%29tvB%5E%3C%3B2Jm3@artifactory.tools.digital.engie.com/artifactory/api/pypi/all-team-pypi-prod/simple
```
