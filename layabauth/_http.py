from typing import Mapping

import requests
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
def keys(jwks_uri: str) -> str:
    try:
        response = requests.get(jwks_uri, verify=False)
    except requests.RequestException as e:
        raise exceptions.JOSEError(
            f"{type(e).__name__} error while retrieving keys: {str(e)}"
        )

    if not response:
        raise exceptions.JOSEError(
            f"HTTP {response.status_code} error while retrieving keys: {response.text}"
        )

    return response.text
