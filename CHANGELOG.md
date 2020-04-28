# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

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

[Unreleased]: https://github.com/Colin-b/layabauth/compare/v4.0.1...HEAD
[4.0.1]: https://github.com/Colin-b/layabauth/compare/v4.0.0...v4.0.1
[4.0.0]: https://github.com/Colin-b/layabauth/compare/v3.2.0...v4.0.0
[3.2.0]: https://github.com/Colin-b/layabauth/releases/tag/v3.2.0
