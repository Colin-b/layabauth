# Python Common Server Changelog #

List all changes in various categories:
* Release notes: Contains all worth noting changes (breaking changes mainly)
* Enhancements
* Bug fixes
* Known issues

## Version 14.1.0 (2019-03-21) ##

### Enhancements ###

- Update dependencies to latest version (pandas 0.24.2 PyYaml 5.1).

## Version 14.0.0 (2019-03-19) ##

### Release notes ###

- /changelog endpoint now returns an interpreted Markdown changelog as JSON (so that it can be processed by clients).

## Version 13.3.2 (2019-03-08) ##

### Bug fixes ###

- Celery now handle path parameters (in result and status endpoint, as well as in custom response callable). 

## Version 13.3.1 (2019-01-26) ##

### Bug fixes ###

- Exception raised by the celery task are now propagated to the service when requesting the result. 

## Version 13.3.0 (2019-02-22) ##

### Enhancements ###

- Update dependencies to latest version (pycommon-test 5.1.0, oauth2helper 1.5.0, redis 3.2.0).

## Version 13.2.3 (2019-02-05) ##

### Bug fixes ###

- Avoid importing requests in health.py (preventing use of status function).

## Version 13.2.2 (2019-01-30) ##

### Bug fixes ###

- Avoid sending bytes in redis health details (as it cannot be serialized to JSON).

## Version 13.2.1 (2019-01-30) ##

### Bug fixes ###

- Prevent redis and celery health check to throw exception.

## Version 13.2.0 (2019-01-29) ##

### Enhancements ###

- Celery common does not expose celery_result variable, use celery.result instead.

## Version 13.1.0 (2019-01-28) ##

### Enhancements ###

- Rely on latest version of redis.
- Return HTTP 429 in case of warning to trigger a Consul warning. (was a 200 previously)
- Add a new /changelog endpoint within monitoring section for all services.
- Add health check for Redis
- Allow to consider HTTP health check failure as pass or warn status (instead of fail as default).

## Version 13.0.0 (2019-01-23) ##

### Release notes ###

- Change on async api: when you start a task it now replies with a JSON body with 2 keys: task_id and url.
- Move module attribute how_to_get_async_status_doc to an instance attribute of AsyncNamespaceProxy.
- Instead of using celery_common.how_to_get_async_status_doc (or importing from celery_common import how_to_get_async_status_doc) use async_ns_proxy.how_to_get_async_status_doc.

## Version 12.13.0 (2019-01-22) ##

### Enhancements ###

- Add x-server-environment to swagger.json info section
 
## Version 12.12.0 (2019-01-15) ##

### Enhancements ###

- Add celery msgpack module.
- Update dependencies to latest version (pycommon_test 5.0.0)
- Add celery health_details function to check celery health.

## Version 12.11.0 (2019-01-11) ##

### Enhancements ###

- New http module with pandas http response helpers

## Version 12.10.0 (2019-01-10) ##

### Enhancements ###

- Update dependencies to latest version (pycommon_test 4.10.0)

## Version 12.9.0 (2019-01-09) ##

### Enhancements ###

- Update dependencies to latest version (pycommon_test 4.9.0, pysmb 1.1.27)

## Version 12.8.1 (2019-01-03) ##

### Bug fixes ###

- Ensure that health checker manage non json response by default.
- Ensure that content type 'application/health+json' is recognized as json response.

## Version 12.8.0 (2018-12-20) ##

### Enhancements ###

- Allow to provide an additional parameter to_response to an async route to manipulate async task result.

## Version 12.7.0 (2018-12-19) ##

### Enhancements ###

- Update dependencies to latest version (pycommon_test 4.8.0)

## Version 12.6.0 (2018-12-14) ##

### Enhancements ###

- Update dependencies to latest version (pycommon_test 4.7.0)

## Version 12.5.0 (2018-12-14) ##

### Enhancements ###

- Update dependencies to latest version (pycommon_test 4.6.0, oauth2helper 1.4.0)

## Version 12.4.1 (2018-12-13) ##

### Bug fixes ###

- Ensure that health check is performed in less than 6 seconds (1 second to connect at max and 5 second to retrieve data at max).

## Version 12.4.0 (2018-12-13) ##

### Enhancements ###

- Update dependencies to latest version (pycommon_test 4.5.0)

## Version 12.3.0 (2018-12-12) ##

### Enhancements ###

- Update dependencies to latest version (pycommon_test 4.4.0)

## Version 12.2.0 (2018-12-12) ##

### Enhancements ###

- Update dependencies to latest version (pycommon_test 4.3.0, requests 2.21.0)

## Version 12.1.0 (2018-12-06) ##

### Enhancements ###

- Response Model is now optional on asynchronous route.

## Version 12.0.0 (2018-12-05) ##

### Release notes ###

- Rename rest_helper module into health.
- Rename rest_helper.health_details into health.http_details.

### Enhancements ###

- Add a new health.status function returning status according to a list of statuses.

## Version 11.2.0 (2018-12-04) ##

### Enhancements ###

- Update dependencies to latest version (pycommon_test 4.1.0)

## Version 11.1.0 (2018-12-03) ##

### Enhancements ###

- Update dependencies to latest version (pycommon_test 4.0.0)

## Version 11.0.0 (2018-11-30) ##

### Release notes ###

- Rename how_to_get_celery_status into how_to_get_async_status

### Enhancements ###

- how_to_get_async_status_doc is now available to properly document asynchronous endpoints

### Bug fixes ###

- OpenAPI definition now return an accurate description of async tasks.

## Version 10.1.1 (2018-11-30) ##

### Bug fixes ###

- Health to follow namespace documentation convention.

## Version 10.1.0 (2018-11-29) ##

### Enhancements ###

- Add celery support via celery_common module
- New version of pycommon-test with celery_mock

## Version 10.0.0 (2018-11-29) ##

### Release notes ###

- create_api now expect a file path as first parameter instead of the file name.

## Version 9.0.0 (2018-11-29) ##

### Release notes ###

- The function used by add_monitoring_namespace now expect a tuple bool, dict instead of 3 dicts.

### Enhancements ###

- Add a new rest_helper to retrieve details from another API.

## Version 8.0.0 (2018-11-26) ##

### Release notes ###

- add_monitoring_namespace no longer takes a controller. You need to provide two parameters instead of 3. The API and the function returning details.
- Default post, put and delete responses do not exists anymore. Replaced by 
  * created_response(url)
  * updated_response(url)
  * deleted_response
- Default models for post, put, delete responses do not exists anymore. Replaced by
  * created_response_doc(api)
  * updated_response_doc(api)
  * deleted_response_doc

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
