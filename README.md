<h2 align="center">Python Common Server Module</h2>

<p align="center">
<a href="https://github.com/ambv/black"><img alt="Code style: black" src="https://img.shields.io/badge/code%20style-black-000000.svg"></a>
<a href='https://pse.tools.digital.engie.com/drm-all.gem/job/team/view/Python%20modules/job/pycommon_server/job/master/'><img src='https://pse.tools.digital.engie.com/drm-all.gem/buildStatus/icon?job=team/pycommon_server/master'></a>
</p>

This package provides the following features:

## Asynchronous REST API ##

Thanks to Celery, your REST API can now expose asynchronous endpoints.

You will find more details in pycommon_server.celery_common module.

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

Importing pycommon_server.flask_restplus_common will make sure that every flask request is loggued on reception. 

```python
import pycommon_server.flask_restplus_common
```

## Health check ##

If your REST API is calling other REST API(s) then your health check should ensure that those APIs can be reached.

You will find more details in pycommon_server.health module.

## Accessing Windows from Linux ##

If you need to access Windows computers from your REST API hosted on Linux.

You will find more details in pycommon_server.windows module.

Contributing
------------

Everyone is free to contribute on this project.

Before creating an issue please make sure that it was not already reported.

Project follow "Black" code formatting: https://black.readthedocs.io/en/stable/

To integrate it within Pycharm: https://black.readthedocs.io/en/stable/editor_integration.html#pycharm

To add the pre-commit hook, after the installation run: **pre-commit install**
