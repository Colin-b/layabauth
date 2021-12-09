# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [5.1.1] - 2021-12-07
### Changed
- Update [`httpx`](https://github.com/encode/httpx/blob/master/CHANGELOG.md) version from `0.17.*` to `0.19.*`
- Update [`pytest-httpx`](https://github.com/Colin-b/pytest_httpx/blob/master/CHANGELOG.md) version from `0.11.*` to `0.13.*`.
- Update [`flask_restx`](https://github.com/python-restx/flask-restx/blob/master/CHANGELOG.rst) version from `0.2.*` to `0.5.*`

## [5.1.0] - 2021-03-01
### Changed
- Update [`httpx`](https://github.com/encode/httpx/blob/master/CHANGELOG.md) version from `0.16.*` to `0.17.*`
- Update [`pytest-httpx`](https://github.com/Colin-b/pytest_httpx/blob/master/CHANGELOG.md) version from `0.10.*` to `0.11.*`.
- Update [`starlette`](https://www.starlette.io/release-notes/) version from `0.13.*` to `0.14.*`.

## [5.0.1] - 2020-11-17
### Added
- Add explicit support for python `3.9`.

### Changed
- Update [`black`](https://github.com/psf/black/blob/master/CHANGES.md) version from `master` to `20.8b1`.
- Use `httpx` instead of `requests` to query keys.
- Testing mock does not rely on `pytest-responses` anymore.

### Fixed
- Verify SSL certificate by default.

## [5.0.0] - 2020-05-29
### Changed
- layabauth.authorizations now requires scopes to be provided as a dictionary inside scopes parameter instead of kwargs.

### Fixed
- Allow to provide scopes that cannot be stored as python variables (such as names containing `.` (dots) or `-` (minus) symbols).

### Added
- `layabauth.flask.requires_scopes` function to ensure that expected scopes are received.

## [4.0.1] - 2020-04-28
### Fixed
- Drop oauth2helper in favor of python-jose to handle all kind of tokens.

### Changed
- `identity_provider_url` has been renamed to `jwks_uri` to match the key in .well-known
- `jwks_uri` pytest fixture needs to be provided in addition to `token_body`.
- Flask tests will require a fake token to be provided in headers (unless you want to test behavior without providing a token).

## [4.0.0] - 2020-04-20
### Changed
- Flask specifics are now within layabauth.flask.
- flask.g.current_user does not exists, instead, the validated token and the decoded token body are available in flask.g.token and flask.g.token_body
- `upn` field is not expected in token anymore. It is now up to the user to select what information they want to extract from the decoded token body.
- `UserIdFilter` class now requires `token_field_name` parameter to know what token body field value must be set inside `user_id`.
- `auth_mock` fixture now expects `token_body` fixture providing the decoded token body instead of `upn` fixture.

## [3.2.0] - 2019-12-02
### Added
- Initial release.

[Unreleased]: https://github.com/Colin-b/layabauth/compare/v5.1.0...HEAD
[5.1.0]: https://github.com/Colin-b/layabauth/compare/v5.0.1...v5.1.0
[5.0.1]: https://github.com/Colin-b/layabauth/compare/v5.0.0...v5.0.1
[5.0.0]: https://github.com/Colin-b/layabauth/compare/v4.0.1...v5.0.0
[4.0.1]: https://github.com/Colin-b/layabauth/compare/v4.0.0...v4.0.1
[4.0.0]: https://github.com/Colin-b/layabauth/compare/v3.2.0...v4.0.0
[3.2.0]: https://github.com/Colin-b/layabauth/releases/tag/v3.2.0
