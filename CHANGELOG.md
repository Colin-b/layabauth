# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [2.0.0] - 2019-08-06
### Changed
- Update oauth2helper to version 3.0.1
- requires_authentication now requires identity provider URL as parameter.
- Engie specifics are not stored anymore and must be provided when calling authorizations()
- User identifier is now extracted following the same way authorization is.
- Add a pytest fixture to mock authentication

## [1.0.0] - 2019-08-01
### Changed
- Initial release.

[Unreleased]: https://github.tools.digital.engie.com/GEM-Py/layabauth/compare/v2.0.0...HEAD
[2.0.0]: https://github.tools.digital.engie.com/GEM-Py/layabauth/compare/v1.0.0...v2.0.0
[1.0.0]: https://github.tools.digital.engie.com/GEM-Py/layabauth/releases/tag/v1.0.0
