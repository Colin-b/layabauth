# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [16.0.0] - 2019-04-11
### Changed
- Version is now extracted from version.py instead of _version.py
- Version is now in a public file.

## [15.2.0] - 2019-04-01
### Changed
- Update celery to version 4.3.0.
- Update pre-commit to version 1.15.0.

## [15.1.0] - 2019-04-01
### Changed
- Follow keep a changelog format.

## [15.0.0] - 2019-03-27
### Changed
- celery_common.redis_health_details function now takes a single argument being the configuration as a dict.
- celery_common.health_details function does not take arguments anymore.

### Added
- Update dependencies to latest version (redis 3.2.1, celery 4.2.2, pre-commit 1.14.4, pycommon_test 5.2.0).
- Celery health check now ping only relevant workers.
- namespace is not read anymore from celery configuration.
- Add more common arguments to celery application.

### Fixed
- Properly retrieve the environment value used to identify celery production worker namespace.

## [14.1.0] - 2019-03-21
### Added
- Update dependencies to latest version (pandas 0.24.2 PyYaml 5.1).

## [14.0.0] - 2019-03-19
### Changed
- /changelog endpoint now returns an interpreted Markdown changelog as JSON (so that it can be processed by clients).

## [13.3.2] - 2019-03-08
### Fixed
- Celery now handle path parameters (in result and status endpoint, as well as in custom response callable).

## [13.3.1] - 2019-01-26
### Fixed
- Exception raised by the celery task are now propagated to the service when requesting the result.

## [13.3.0] - 2019-02-22
### Added
- Update dependencies to latest version (pycommon-test 5.1.0, oauth2helper 1.5.0, redis 3.2.0).

## [13.2.3] - 2019-02-05
### Fixed
- Avoid importing requests in health.py (preventing use of status function).

## [13.2.2] - 2019-01-30
### Fixed
- Avoid sending bytes in redis health details (as it cannot be serialized to JSON).

## [13.2.1] - 2019-01-30
### Fixed
- Prevent redis and celery health check to throw exception.

## [13.2.0] - 2019-01-29
### Added
- Celery common does not expose celery_result variable, use celery.result instead.

## [13.1.0] - 2019-01-28
### Added
- Rely on latest version of redis.
- Return HTTP 429 in case of warning to trigger a Consul warning. (was a 200 previously)
- Add a new /changelog endpoint within monitoring section for all services.
- Add health check for Redis
- Allow to consider HTTP health check failure as pass or warn status (instead of fail as default).

## [13.0.0] - 2019-01-23
### Changed
- Change on async api: when you start a task it now replies with a JSON body with 2 keys: task_id and url.
- Move module attribute how_to_get_async_status_doc to an instance attribute of AsyncNamespaceProxy.
- Instead of using celery_common.how_to_get_async_status_doc (or importing from celery_common import how_to_get_async_status_doc) use async_ns_proxy.how_to_get_async_status_doc.

## [12.13.0] - 2019-01-22
### Added
- Add x-server-environment to swagger.json info section

## [12.12.0] - 2019-01-15
### Added
- Add celery msgpack module.
- Update dependencies to latest version (pycommon_test 5.0.0)
- Add celery health_details function to check celery health.

## [12.11.0] - 2019-01-11
### Added
- New http module with pandas http response helpers

## [12.10.0] - 2019-01-10
### Added
- Update dependencies to latest version (pycommon_test 4.10.0)

## [12.9.0] - 2019-01-09
### Added
- Update dependencies to latest version (pycommon_test 4.9.0, pysmb 1.1.27)

## [12.8.1] - 2019-01-03
### Fixed
- Ensure that health checker manage non json response by default.
- Ensure that content type 'application/health+json' is recognized as json response.

## [12.8.0] - 2018-12-20
### Added
- Allow to provide an additional parameter to_response to an async route to manipulate async task result.

## [12.7.0] - 2018-12-19
### Added
- Update dependencies to latest version (pycommon_test 4.8.0)

## [12.6.0] - 2018-12-14
### Added
- Update dependencies to latest version (pycommon_test 4.7.0)

## [12.5.0] - 2018-12-14
### Added
- Update dependencies to latest version (pycommon_test 4.6.0, oauth2helper 1.4.0)

## [12.4.1] - 2018-12-13
### Fixed
- Ensure that health check is performed in less than 6 seconds (1 second to connect at max and 5 second to retrieve data at max).

## [12.4.0] - 2018-12-13
### Added
- Update dependencies to latest version (pycommon_test 4.5.0)

## [12.3.0] - 2018-12-12
### Added
- Update dependencies to latest version (pycommon_test 4.4.0)

## [12.2.0] - 2018-12-12
### Added
- Update dependencies to latest version (pycommon_test 4.3.0, requests 2.21.0)

## [12.1.0] - 2018-12-06
### Added
- Response Model is now optional on asynchronous route.

## [12.0.0] - 2018-12-05
### Changed
- Rename rest_helper module into health.
- Rename rest_helper.health_details into health.http_details.

### Added
- Add a new health.status function returning status according to a list of statuses.

## [11.2.0] - 2018-12-04
### Added
- Update dependencies to latest version (pycommon_test 4.1.0)

## [11.1.0] - 2018-12-03
### Added
- Update dependencies to latest version (pycommon_test 4.0.0)

## [11.0.0] - 2018-11-30
### Changed
- Rename how_to_get_celery_status into how_to_get_async_status

### Added
- how_to_get_async_status_doc is now available to properly document asynchronous endpoints

### Fixed
- OpenAPI definition now return an accurate description of async tasks.

## [10.1.1] - 2018-11-30
### Fixed
- Health to follow namespace documentation convention.

## [10.1.0] - 2018-11-29
### Added
- Add celery support via celery_common module
- New version of pycommon-test with celery_mock

## [10.0.0] - 2018-11-29
### Changed
- create_api now expect a file path as first parameter instead of the file name.

## [9.0.0] - 2018-11-29
### Changed
- The function used by add_monitoring_namespace now expect a tuple bool, dict instead of 3 dicts.

### Added
- Add a new rest_helper to retrieve details from another API.

## [8.0.0] - 2018-11-26
### Changed
- add_monitoring_namespace no longer takes a controller. You need to provide two parameters instead of 3. The API and the function returning details.
- Default post, put and delete responses do not exists anymore. Replaced by
* created_response(url)
* updated_response(url)
* deleted_response
- Default models for post, put, delete responses do not exists anymore. Replaced by
* created_response_doc(api)
* updated_response_doc(api)
* deleted_response_doc

### Added
- Add method to create Flask Application / Flask RestPlus API with additional options:
* HTTP Gzip Compression (defaulted to false, provide list of mimetype to compress to enable)
* Reverse Proxy (defaulted to true, allow Swagger UI behind reverse proxy)
* Cors (defaulted to true, allow cross origin)

## [7.0.1] - 2018-11-16
### Fixed
- Avoid useless new line character in description of health endpoint.

## [7.0.0] - 2018-11-16
### Changed
- Health controller is not instantiated anymore before calling get method. To upgrade to this version you will need to:
Switch your controllers.Health.get method to a classmethod or instantiate controllers.Health when providing it to
add_monitoring_namespace method

- Configuration is not loaded based on ENVIRONMENT environment variable anymore. It is only loaded based on
SERVER_ENVIRONMENT environment variable. It should not impact anyone but clients relying on old deployment scripts
or source docker image might want to ensure they set this variable properly.

## [6.2.0] - 2018-11-16
### Added
- Update dependencies to latest version (celery 4.2.1, pycommon_test 2.0.0 and oauth2helper 1.3.0)

### Fixed
- Add oauth2helper dependency to testing.

## [6.1.0] - 2018-11-13
### Added
- Add celery request id if available (and flask request id is not)

## [6.0.1] - 2018-10-30
### Fixed
- Update dependencies to latest version.

## [6.0.0] - 2018-10-10
### Changed
- add_monitoring_namespace second parameter is now all the error handlers.

## [5.0.0] - 2018-10-10
### Changed
- OAuth2 authentication token is now extracted from Authorization header (Bearer {token}).

### Fixed
- Update dependencies to latest version.

## [4.1.2] - 2018-10-01
### Fixed
- Update dependencies.

## [4.1.1] - 2018-10-01
### Fixed
- [Windows] refactor rename function.
- Update dependencies to latest version.

## [4.1.0] - 2018-09-24
### Added
- [Windows] added a rename function.
- Update dependencies to latest version.

## [4.0.1] - 2018-08-30
### Fixed
- Update dependencies to latest version.

## [4.0.0] - 2018-08-23
### Changed
- Default handler has been extracted to pycommon-error module.

## [3.3.3] - 2018-08-20
### Fixed
- Update dependencies to latest version.

## [3.3.2] - 2018-08-10
### Fixed
- Ensure that opened resources are closed (when using move_file).
- Update PyYAML to latest version (3.13).
- Update Flask-RestPlus to latest version (0.11.0).
- Update pysmb to latest version (1.1.25)

## [3.3.1] - 2018-06-27
### Fixed
- Rely on PyYaml instead of pyaml (fix version of PyYaml instead).

## [3.3.0] - 2018-06-08
### Added
- Provide a windows module for file handling from GNU/Linux.

## [3.2.2] - 2018-05-03
### Fixed
- Handle token with underscore character.

## [3.2.1] - 2018-03-29
### Fixed
- LogRequestDetails and RequiresAuthentication have been renamed into log_request_details and requires_authentication.
- Additional decorators can now be used after using LogRequestDetails or RequiresAuthentication.

## [3.2.0] - 2018-03-02
### Added
- Introduce new decorator to authenticate user and methods to provide authorization in swagger.

## [3.1.0] - 2017-11-14
### Added
- Introduce pycommon_server.logging_filter module allowing to display request identifier or user identifier in logs.

## [3.0.0] - 2017-10-23
### Changed
- Health controller should now contains a instead of a marshaller method.

## [2.6.0] - 2017-10-17
### Added
- Register LogRequestDetails as Flask-RestPlus decorator when importing flask_restplus_common.

## [2.5.0] - 2017-10-17
### Added
- Introduce LogRequestDetails decorator.

## [2.4.0] - 2017-10-06
### Added
- SERVER_ENVIRONMENT can also be used and has precedence on ENVIRONMENT

## [2.3.0] - 2017-10-06
### Added
- Introduce configuration.load() method to use for standard configurations loading.

## [2.2.0] - 2017-09-29
### Added
- Add test cases.

## [2.1.0] - 2017-09-29
### Added
- Health check Swagger documentation does not reference Consul anymore.

## [2.0.0] - 2017-09-28
### Changed
- Exception are logged on server side as well with all information.
- Status code 500 (Server error) is now returned in case of an unhandled Exception (instead of 400 - Client error, previously).

## [1.1.0] - 2017-09-27
### Changed
- Dependencies are now set to flask-restplus 0.10.1 and pyaml 17.8.0.

## [1.0.0] - 2017-09-27
### Changed
- Initial release.

[Unreleased]: https://github.tools.digital.engie.com/GEM-Py/pycommon-server/compare/v16.0.0...HEAD
[16.0.0]: https://github.tools.digital.engie.com/GEM-Py/pycommon-server/compare/v15.2.0...v16.0.0
[15.2.0]: https://github.tools.digital.engie.com/GEM-Py/pycommon-server/compare/v15.1.0...v15.2.0
[15.1.0]: https://github.tools.digital.engie.com/GEM-Py/pycommon-server/compare/v15.0.0...v15.1.0
[15.0.0]: https://github.tools.digital.engie.com/GEM-Py/pycommon-server/compare/v14.1.0...v15.0.0
[14.1.0]: https://github.tools.digital.engie.com/GEM-Py/pycommon-server/compare/v14.0.0...v14.1.0
[14.0.0]: https://github.tools.digital.engie.com/GEM-Py/pycommon-server/compare/v13.3.2...v14.0.0
[13.3.2]: https://github.tools.digital.engie.com/GEM-Py/pycommon-server/compare/v13.3.1...v13.3.2
[13.3.1]: https://github.tools.digital.engie.com/GEM-Py/pycommon-server/compare/v13.3.0...v13.3.1
[13.3.0]: https://github.tools.digital.engie.com/GEM-Py/pycommon-server/compare/v13.2.3...v13.3.0
[13.2.3]: https://github.tools.digital.engie.com/GEM-Py/pycommon-server/compare/v13.2.2...v13.2.3
[13.2.2]: https://github.tools.digital.engie.com/GEM-Py/pycommon-server/compare/v13.2.1...v13.2.2
[13.2.1]: https://github.tools.digital.engie.com/GEM-Py/pycommon-server/compare/v13.2.0...v13.2.1
[13.2.0]: https://github.tools.digital.engie.com/GEM-Py/pycommon-server/compare/v13.1.0...v13.2.0
[13.1.0]: https://github.tools.digital.engie.com/GEM-Py/pycommon-server/compare/v13.0.0...v13.1.0
[13.0.0]: https://github.tools.digital.engie.com/GEM-Py/pycommon-server/compare/v12.13.0...v13.0.0
[12.13.0]: https://github.tools.digital.engie.com/GEM-Py/pycommon-server/compare/v12.12.0...v12.13.0
[12.12.0]: https://github.tools.digital.engie.com/GEM-Py/pycommon-server/compare/v12.11.0...v12.12.0
[12.11.0]: https://github.tools.digital.engie.com/GEM-Py/pycommon-server/compare/v12.10.0...v12.11.0
[12.10.0]: https://github.tools.digital.engie.com/GEM-Py/pycommon-server/compare/v12.9.0...v12.10.0
[12.9.0]: https://github.tools.digital.engie.com/GEM-Py/pycommon-server/compare/v12.8.1...v12.9.0
[12.8.1]: https://github.tools.digital.engie.com/GEM-Py/pycommon-server/compare/v12.8.0...v12.8.1
[12.8.0]: https://github.tools.digital.engie.com/GEM-Py/pycommon-server/compare/v12.7.0...v12.8.0
[12.7.0]: https://github.tools.digital.engie.com/GEM-Py/pycommon-server/compare/v12.6.0...v12.7.0
[12.6.0]: https://github.tools.digital.engie.com/GEM-Py/pycommon-server/compare/v12.5.0...v12.6.0
[12.5.0]: https://github.tools.digital.engie.com/GEM-Py/pycommon-server/compare/v12.4.1...v12.5.0
[12.4.1]: https://github.tools.digital.engie.com/GEM-Py/pycommon-server/compare/v12.4.0...v12.4.1
[12.4.0]: https://github.tools.digital.engie.com/GEM-Py/pycommon-server/compare/v12.3.0...v12.4.0
[12.3.0]: https://github.tools.digital.engie.com/GEM-Py/pycommon-server/compare/v12.2.0...v12.3.0
[12.2.0]: https://github.tools.digital.engie.com/GEM-Py/pycommon-server/compare/v12.1.0...v12.2.0
[12.1.0]: https://github.tools.digital.engie.com/GEM-Py/pycommon-server/compare/v12.0.0...v12.1.0
[12.0.0]: https://github.tools.digital.engie.com/GEM-Py/pycommon-server/compare/v11.2.0...v12.0.0
[11.2.0]: https://github.tools.digital.engie.com/GEM-Py/pycommon-server/compare/v11.1.0...v11.2.0
[11.1.0]: https://github.tools.digital.engie.com/GEM-Py/pycommon-server/compare/v11.0.0...v11.1.0
[11.0.0]: https://github.tools.digital.engie.com/GEM-Py/pycommon-server/compare/v10.1.1...v11.0.0
[10.1.1]: https://github.tools.digital.engie.com/GEM-Py/pycommon-server/compare/v10.1.0...v10.1.1
[10.1.0]: https://github.tools.digital.engie.com/GEM-Py/pycommon-server/compare/v10.0.0...v10.1.0
[10.0.0]: https://github.tools.digital.engie.com/GEM-Py/pycommon-server/compare/v9.0.0...v10.0.0
[9.0.0]: https://github.tools.digital.engie.com/GEM-Py/pycommon-server/compare/v8.0.0...v9.0.0
[8.0.0]: https://github.tools.digital.engie.com/GEM-Py/pycommon-server/compare/v7.0.1...v8.0.0
[7.0.1]: https://github.tools.digital.engie.com/GEM-Py/pycommon-server/compare/v7.0.0...v7.0.1
[7.0.0]: https://github.tools.digital.engie.com/GEM-Py/pycommon-server/compare/v6.2.0...v7.0.0
[6.2.0]: https://github.tools.digital.engie.com/GEM-Py/pycommon-server/compare/v6.1.0...v6.2.0
[6.1.0]: https://github.tools.digital.engie.com/GEM-Py/pycommon-server/compare/v6.0.1...v6.1.0
[6.0.1]: https://github.tools.digital.engie.com/GEM-Py/pycommon-server/compare/v6.0.0...v6.0.1
[6.0.0]: https://github.tools.digital.engie.com/GEM-Py/pycommon-server/compare/v5.0.0...v6.0.0
[5.0.0]: https://github.tools.digital.engie.com/GEM-Py/pycommon-server/compare/v4.1.2...v5.0.0
[4.1.2]: https://github.tools.digital.engie.com/GEM-Py/pycommon-server/compare/v4.1.1...v4.1.2
[4.1.1]: https://github.tools.digital.engie.com/GEM-Py/pycommon-server/compare/v4.1.0...v4.1.1
[4.1.0]: https://github.tools.digital.engie.com/GEM-Py/pycommon-server/compare/v4.0.1...v4.1.0
[4.0.1]: https://github.tools.digital.engie.com/GEM-Py/pycommon-server/compare/v4.0.0...v4.0.1
[4.0.0]: https://github.tools.digital.engie.com/GEM-Py/pycommon-server/compare/v3.3.3...v4.0.0
[3.3.3]: https://github.tools.digital.engie.com/GEM-Py/pycommon-server/compare/v3.3.2...v3.3.3
[3.3.2]: https://github.tools.digital.engie.com/GEM-Py/pycommon-server/compare/v3.3.1...v3.3.2
[3.3.1]: https://github.tools.digital.engie.com/GEM-Py/pycommon-server/compare/v3.3.0...v3.3.1
[3.3.0]: https://github.tools.digital.engie.com/GEM-Py/pycommon-server/compare/v3.2.2...v3.3.0
[3.2.2]: https://github.tools.digital.engie.com/GEM-Py/pycommon-server/compare/v3.2.1...v3.2.2
[3.2.1]: https://github.tools.digital.engie.com/GEM-Py/pycommon-server/compare/v3.2.0...v3.2.1
[3.2.0]: https://github.tools.digital.engie.com/GEM-Py/pycommon-server/compare/v3.1.0...v3.2.0
[3.1.0]: https://github.tools.digital.engie.com/GEM-Py/pycommon-server/compare/v3.0.0...v3.1.0
[3.0.0]: https://github.tools.digital.engie.com/GEM-Py/pycommon-server/compare/v2.6.0...v3.0.0
[2.6.0]: https://github.tools.digital.engie.com/GEM-Py/pycommon-server/compare/v2.5.0...v2.6.0
[2.5.0]: https://github.tools.digital.engie.com/GEM-Py/pycommon-server/compare/v2.4.0...v2.5.0
[2.4.0]: https://github.tools.digital.engie.com/GEM-Py/pycommon-server/compare/v2.3.0...v2.4.0
[2.3.0]: https://github.tools.digital.engie.com/GEM-Py/pycommon-server/compare/v2.2.0...v2.3.0
[2.2.0]: https://github.tools.digital.engie.com/GEM-Py/pycommon-server/compare/v2.1.0...v2.2.0
[2.1.0]: https://github.tools.digital.engie.com/GEM-Py/pycommon-server/compare/v2.0.0...v2.1.0
[2.0.0]: https://github.tools.digital.engie.com/GEM-Py/pycommon-server/compare/v1.1.0...v2.0.0
[1.1.0]: https://github.tools.digital.engie.com/GEM-Py/pycommon-server/compare/v1.0.0...v1.1.0
[1.0.0]: https://github.tools.digital.engie.com/GEM-Py/pycommon-server/releases/tag/v1.0.0
