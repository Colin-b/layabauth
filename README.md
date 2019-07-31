<h2 align="center">Python Common Server Module</h2>

<p align="center">
<a href="https://github.com/psf/black"><img alt="Code style: black" src="https://img.shields.io/badge/code%20style-black-000000.svg"></a>
<a href='https://pse.tools.digital.engie.com/drm-all.gem/job/team/view/Python%20modules/job/pycommon_server/job/master/'><img src='https://pse.tools.digital.engie.com/drm-all.gem/buildStatus/icon?job=team/pycommon_server/master'></a>
<a href='https://pse.tools.digital.engie.com/drm-all.gem/job/team/view/Python%20modules/job/pycommon_server/job/master/cobertura/'><img src='https://pse.tools.digital.engie.com/drm-all.gem/buildStatus/icon?job=team/pycommon_server/master&config=testCoverage'></a>
<a href='https://pse.tools.digital.engie.com/drm-all.gem/job/team/view/Python%20modules/job/pycommon_server/job/master/lastSuccessfulBuild/testReport/'><img src='https://pse.tools.digital.engie.com/drm-all.gem/buildStatus/icon?job=team/pycommon_server/master&config=testCount'></a>
</p>

This package provides the following features:

## YAML Configuration ##

API configuration and logging configuration can be standardized.

You will find more details in pycommon_server.configuration module.

### Loading configuration ###

```python
from pycommon_server.configuration import load

# Load logging and service configuration
service_configuration = load('path/to/a/file/in/module/folder')
```

## Flask RestPlus ##

The way your REST API behaves can be standardized.

You will find more details in pycommon_server.flask_restplus_common module.

### Default behavior ###

Importing pycommon_server.monitoring will make sure that every flask request is loggued on reception. 

```python
import pycommon_server.monitoring
```

## How to install
1. [python 3.7+](https://www.python.org/downloads/) must be installed
2. Use pip to install module:
```sh
python -m pip install pycommon_server -i https://all-team-remote:tBa%40W%29tvB%5E%3C%3B2Jm3@artifactory.tools.digital.engie.com/artifactory/api/pypi/all-team-pypi-prod/simple
```
