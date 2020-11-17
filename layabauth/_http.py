from typing import Mapping

import httpx
from jose import jwt, exceptions


def _get_token(headers: Mapping[str, str]):
    authorization = headers.get("Authorization")
    if authorization and authorization.startswith("Bearer "):
        return authorization[7:]


def validate(token: str, key: str) -> dict:
    return jwt.decode(
        token=token, key=key, algorithms=["RS256"], options={"verify_aud": False}
    )


# TODO Cache keys for faster token validation
def keys(client: httpx.Client, jwks_uri: str) -> str:
    try:
        response = client.get(jwks_uri)
    except httpx.HTTPError as e:
        raise exceptions.JOSEError(
            f"{type(e).__name__} error while retrieving keys: {str(e)}"
        )

    if response.is_error:
        raise exceptions.JOSEError(
            f"HTTP {response.status_code} error while retrieving keys: {response.text}"
        )

    return response.text
