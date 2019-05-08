<h2 align="center">Python Common Server Module</h2>

<p align="center">
<a href="https://github.com/ambv/black"><img alt="Code style: black" src="https://img.shields.io/badge/code%20style-black-000000.svg"></a>
<a href='https://pse.tools.digital.engie.com/drm-all.gem/job/team/view/Python%20modules/job/pycommon_server/job/master/'><img src='https://pse.tools.digital.engie.com/drm-all.gem/buildStatus/icon?job=team/pycommon_server/master'></a>
</p>

This package provides the following features:

## Asynchronous REST API ##

Your REST API can expose asynchronous endpoints.

Chose either Celery or Huey (our favourite).

You will find more details in pycommon_server.celery_common and pycommon_server.huey_common modules.

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
