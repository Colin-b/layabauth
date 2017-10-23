# Python Common Server Changelog #

List all changes in various categories:
* Release notes: Contains all worth noting changes (breaking changes mainly)
* Enhancements
* Bug fixes
* Known issues

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
