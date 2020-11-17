from typing import Optional, Tuple

import httpx
from starlette.authentication import (
    AuthenticationBackend,
    AuthCredentials,
    BaseUser,
    AuthenticationError,
)
from starlette.requests import Request
from jose import exceptions

from layabauth import _http


class OAuth2IdTokenBackend(AuthenticationBackend):
    """
    Handle authentication via OAuth2 id-token (implicit flow, authorization code, with or without PKCE)
    """

    def __init__(
        self, jwks_uri: str, create_user: callable, scopes: callable, **httpx_kwargs
    ):
        """
        :param jwks_uri: The JWKs URI as defined in .well-known.
        For more information on JWK, refer to https://tools.ietf.org/html/rfc7517
            * Azure Active Directory: https://sts.windows.net/common/discovery/keys
            * Microsoft Identity Platform: https://sts.windows.net/common/discovery/keys
        :param create_user: callable receiving the token and the decoded token body and returning a starlette.BaseUser instance.
        :param scopes: callable receiving the token and the decoded token body and returning the list of associated scopes str.
        :param httpx_kwargs: Any other argument will be provided to httpx.Client to be able to retrieve the keys.
        """
        self.jwks_uri = jwks_uri
        self.create_user = create_user
        self.scopes = scopes
        self.httpx_kwargs = httpx_kwargs

    async def authenticate(
        self, request: Request
    ) -> Optional[Tuple["AuthCredentials", "BaseUser"]]:
        token = _http._get_token(request.headers)
        if not token:
            return  # Consider that user is not authenticated

        try:
            with httpx.Client(**self.httpx_kwargs) as client:
                key = _http.keys(client, self.jwks_uri)
            json_body = _http.validate(token, key)
        except exceptions.JOSEError as e:
            raise AuthenticationError(str(e)) from e

        return (
            AuthCredentials(scopes=self.scopes(token=token, token_body=json_body)),
            self.create_user(token=token, token_body=json_body),
        )
