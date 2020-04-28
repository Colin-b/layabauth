from typing import Mapping

import requests
from jose import jwt, exceptions


def _get_token(headers: Mapping[str, str]):
    authorization = headers.get("Authorization")
    if authorization and authorization.startswith("Bearer "):
        return authorization[7:]


def validate(token: str, keys_url: str) -> dict:
    try:
        keys = requests.get(keys_url, verify=False)
    except requests.RequestException as e:
        raise exceptions.JOSEError(
            f"{type(e).__name__} error while retrieving keys: {str(e)}"
        )

    if not keys:
        raise exceptions.JOSEError(
            f"HTTP {keys.status_code} error while retrieving keys: {keys.text}"
        )

    return jwt.decode(
        token=token, key=keys.text, algorithms=["RS256"], options={"verify_aud": False}
    )
