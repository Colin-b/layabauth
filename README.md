# Python Common Server Module #

Provide helper to manipulate server.

## Loading configuration ## 


```python
from pycommon_server.configuration import load

# Load logging and service configuration
service_configuration = load('path/to/a/file/in/module/folder')
```

## Default behavior ##

Importing pycommon_server.flask_restplus_common will make sure that every flask request is loggued on reception. 

```python
import pycommon_server.flask_restplus_common
```
