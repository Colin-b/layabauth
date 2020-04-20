from typing import Optional, Tuple

import jwt
import oauth2helper
from starlette.authentication import (
    AuthenticationBackend,
    AuthCredentials,
    BaseUser,
    AuthenticationError,
)
from starlette.requests import Request

from layabauth._http import _get_token


class OAuth2IdTokenBackend(AuthenticationBackend):
    """
    Handle authentication via OAuth2 id-token (implicit flow, authorization code, with or without PKCE)
    """

    def __init__(
        self, identity_provider_url: str, create_user: callable, scopes: callable
    ):
        """
        :param identity_provider_url: URL to retrieve the keys.
            * Azure Active Directory: https://sts.windows.net/common/discovery/keys
        :param create_user: callable receiving the token and the decoded token body and returning a starlette.BaseUser instance.
        :param scopes: callable receiving the token and the decoded token body and returning the list of associated scopes str.
        """
        self.identity_provider_url = identity_provider_url
        self.create_user = create_user
        self.scopes = scopes

    async def authenticate(
        self, request: Request
    ) -> Optional[Tuple["AuthCredentials", "BaseUser"]]:
        token = _get_token(request.headers)
        if not token:
            return  # Consider that user is not authenticated

        try:
            json_header, json_body = oauth2helper.validate(
                token, self.identity_provider_url
            )
        except jwt.PyJWTError as e:
            raise AuthenticationError(str(e)) from e

        return (
            AuthCredentials(scopes=self.scopes(token=token, token_body=json_body)),
            self.create_user(token=token, token_body=json_body),
        )
