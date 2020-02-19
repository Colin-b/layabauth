from typing import Optional, Tuple

import jwt
from starlette.authentication import (
    AuthenticationBackend,
    AuthCredentials,
    BaseUser,
    SimpleUser,
    AuthenticationError,
)
from starlette.requests import Request

from layabauth._authentication import _get_token, _to_user


class OAuth2IdTokenBackend(AuthenticationBackend):
    """Handle authentication via OAuth2 id-token (implicit flow, authorization code, with or without PKCE)"""

    def __init__(self, identity_provider_url: str, scopes_retrieval: callable):
        """
        :param identity_provider_url: URL to retrieve the keys.
            * Azure Active Directory: https://sts.windows.net/common/discovery/keys
        :param scopes_retrieval: callable receiving the username and returning the list of associated scopes.
        """
        self.identity_provider_url = identity_provider_url
        self.scopes_retrieval = scopes_retrieval

    async def authenticate(
        self, request: Request
    ) -> Optional[Tuple["AuthCredentials", "BaseUser"]]:
        token = _get_token(request.headers)
        if not token:
            return  # Consider that user is not authenticated

        try:
            user = _to_user(token, self.identity_provider_url)
        except (
            jwt.exceptions.InvalidTokenError or jwt.exceptions.InvalidKeyError
        ) as e:
            raise AuthenticationError(str(e)) from e

        return (
            AuthCredentials(scopes=self.scopes_retrieval(user.name)),
            SimpleUser(user.name),
        )
