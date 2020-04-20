from typing import Mapping


def _get_token(headers: Mapping[str, str]):
    authorization = headers.get("Authorization")
    if authorization and authorization.startswith("Bearer "):
        return authorization[7:]
