"""Minimal JWT bearer auth. In production, replace HS256 with a proper IdP."""
from __future__ import annotations
import time
import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from services.common.config import get_settings

bearer = HTTPBearer(auto_error=False)


def issue_token(sub: str, ttl_s: int = 3600) -> str:
    now = int(time.time())
    return jwt.encode(
        {"sub": sub, "iat": now, "exp": now + ttl_s},
        get_settings().jwt_secret,
        algorithm="HS256",
    )


def current_user(creds: HTTPAuthorizationCredentials | None = Depends(bearer)) -> str:
    if creds is None:
        # dev fallback - anonymous user
        return "anon"
    try:
        payload = jwt.decode(creds.credentials, get_settings().jwt_secret, algorithms=["HS256"])
        return payload["sub"]
    except jwt.PyJWTError as e:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, f"bad token: {e}") from e
