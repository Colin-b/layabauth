# Python Common Server Changelog #

List all changes in various categories:
* Release notes: Contains all worth noting changes (breaking changes mainly)
* Enhancements
* Bug fixes
* Known issues

## Version 7.1.0 (2018-11-26) ##

### Enhancements ###

- Add method to create Flask Application / Flask RestPlus API with additional options:
    * HTTP Gzip Compression (defaulted to false, provide list of mimetype to compress to enable)
    * Reverse Proxy (defaulted to true, allow Swagger UI behind reverse proxy)
    * Cors (defaulted to true, allow cross origin)

## Version 7.0.1 (2018-11-16) ##

### Bug fixes ###

- Avoid useless new line character in description of health endpoint.

## Version 7.0.0 (2018-11-16) ##

### Release notes ###

- Health controller is not instantiated anymore before calling get method. To upgrade to this version you will need to:
  Switch your controllers.Health.get method to a classmethod or instantiate controllers.Health when providing it to
  add_monitoring_namespace method
 
- Configuration is not loaded based on ENVIRONMENT environment variable anymore. It is only loaded based on 
  SERVER_ENVIRONMENT environment variable. It should not impact anyone but clients relying on old deployment scripts
  or source docker image might want to ensure they set this variable properly.

## Version 6.2.0 (2018-11-16) ##

### Enhancements ###

- Update dependencies to latest version (celery 4.2.1, pycommon_test 2.0.0 and oauth2helper 1.3.0)

### Bug fixes ###

- Add oauth2helper dependency to testing.

## Version 6.1.0 (2018-11-13) ##

### Enhancements ###

- Add celery request id if available (and flask request id is not)

## Version 6.0.1 (2018-10-30) ##

### Bug fixes ###

- Update dependencies to latest version.

## Version 6.0.0 (2018-10-10) ##

### Release notes ###

- add_monitoring_namespace second parameter is now all the error handlers.

## Version 5.0.0 (2018-10-10) ##

### Release notes ###

- OAuth2 authentication token is now extracted from Authorization header (Bearer {token}).

### Bug fixes ###

- Update dependencies to latest version.

## Version 4.1.2 (2018-10-01) ##

### Bug fixes ###

- Update dependencies.

## Version 4.1.1 (2018-10-01) ##

### Bug fixes ###

- [Windows] refactor rename function.
- Update dependencies to latest version.

## Version 4.1.0 (2018-09-24) ##

### Enhancements ###

- [Windows] added a rename function.
- Update dependencies to latest version.

## Version 4.0.1 (2018-08-30) ##

### Bug fixes ###

- Update dependencies to latest version.

## Version 4.0.0 (2018-08-23) ##

### Release notes ###

- Default handler has been extracted to pycommon-error module.

## Version 3.3.3 (2018-08-20) ##

### Bug fixes ###

- Update dependencies to latest version.

## Version 3.3.2 (2018-08-10) ##

### Bug fixes ###

- Ensure that opened resources are closed (when using move_file).
- Update PyYAML to latest version (3.13).
- Update Flask-RestPlus to latest version (0.11.0).
- Update pysmb to latest version (1.1.25)

## Version 3.3.1 (2018-06-27) ##

### Bug fixes ###

- Rely on PyYaml instead of pyaml (fix version of PyYaml instead).

## Version 3.3.0 (2018-06-08) ##

### Enhancements ###

- Provide a windows module for file handling from GNU/Linux.

## Version 3.2.2 (2018-05-03) ##

### Bug fixes ###

- Handle token with underscore character.

## Version 3.2.1 (2018-03-29) ##

### Bug fixes ###

- LogRequestDetails and RequiresAuthentication have been renamed into log_request_details and requires_authentication.
- Additional decorators can now be used after using LogRequestDetails or RequiresAuthentication.

## Version 3.2.0 (2018-03-02) ##

### Enhancements ###

- Introduce new decorator to authenticate user and methods to provide authorization in swagger.

## Version 3.1.0 (2017-11-14) ##

### Enhancements ###

- Introduce pycommon_server.logging_filter module allowing to display request identifier or user identifier in logs.

## Version 3.0.0 (2017-10-23) ##

### Release notes ###

- Health controller should now contains a instead of a marshaller method.

## Version 2.6.0 (2017-10-17) ##

### Enhancements ###

- Register LogRequestDetails as Flask-RestPlus decorator when importing flask_restplus_common.

## Version 2.5.0 (2017-10-17) ##

### Enhancements ###

- Introduce LogRequestDetails decorator.

## Version 2.4.0 (2017-10-06) ##

### Enhancements ###

- SERVER_ENVIRONMENT can also be used and has precedence on ENVIRONMENT

## Version 2.3.0 (2017-10-06) ##

### Enhancements ###

- Introduce configuration.load() method to use for standard configurations loading.

## Version 2.2.0 (2017-09-29) ##

### Enhancements ###

- Add test cases.

## Version 2.1.0 (2017-09-29) ##

### Enhancements ###

- Health check Swagger documentation does not reference Consul anymore.

## Version 2.0.0 (2017-09-28) ##

### Release notes ###

- Exception are logged on server side as well with all information.
- Status code 500 (Server error) is now returned in case of an unhandled Exception (instead of 400 - Client error, previously).

## Version 1.1.0 (2017-09-27) ##

### Release notes ###

- Dependencies are now set to flask-restplus 0.10.1 and pyaml 17.8.0.

## Version 1.0.0 (2017-09-27) ##

### Release notes ###

- Initial release.
