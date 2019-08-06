# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [2.0.0] - 2019-08-06
### Changed
- Update oauth2helper to version 3.0.1
- authorizations now requires auth_url parameter. To keep previous behavior you should use "https://login.microsoftonline.com/24139d14-c62c-4c47-8bdd-ce71ea1d50cf/oauth2/authorize?nonce=7362CAEA-9CA5-4B43-9BA3-34D7C303EBA7"
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
