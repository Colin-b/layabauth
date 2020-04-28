from typing import Optional, Tuple

from starlette.authentication import (
    AuthenticationBackend,
    AuthCredentials,
    BaseUser,
    AuthenticationError,
)
from starlette.requests import Request
from jose import exceptions

from layabauth._http import _get_token, validate, keys


class OAuth2IdTokenBackend(AuthenticationBackend):
    """
    Handle authentication via OAuth2 id-token (implicit flow, authorization code, with or without PKCE)
    """

    def __init__(self, jwks_uri: str, create_user: callable, scopes: callable):
        """
        :param jwks_uri: The JWKs URI as defined in .well-known.
        For more information on JWK, refer to https://tools.ietf.org/html/rfc7517
            * Azure Active Directory: https://sts.windows.net/common/discovery/keys
            * Microsoft Identity Platform: https://sts.windows.net/common/discovery/keys
        :param create_user: callable receiving the token and the decoded token body and returning a starlette.BaseUser instance.
        :param scopes: callable receiving the token and the decoded token body and returning the list of associated scopes str.
        """
        self.jwks_uri = jwks_uri
        self.create_user = create_user
        self.scopes = scopes

    async def authenticate(
        self, request: Request
    ) -> Optional[Tuple["AuthCredentials", "BaseUser"]]:
        token = _get_token(request.headers)
        if not token:
            return  # Consider that user is not authenticated

        try:
            key = keys(self.jwks_uri)
            json_body = validate(token, key)
        except exceptions.JOSEError as e:
            raise AuthenticationError(str(e)) from e

        return (
            AuthCredentials(scopes=self.scopes(token=token, token_body=json_body)),
            self.create_user(token=token, token_body=json_body),
        )
