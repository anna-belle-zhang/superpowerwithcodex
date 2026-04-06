from __future__ import annotations

from datetime import datetime, timedelta, timezone
from uuid import uuid4

import jwt

SECRET_KEY = "development-secret"
ALGORITHM = "HS256"
TOKEN_TTL_SECONDS = 3600

_USERS = {
    "user@example.com": "correct-password",
}
_REVOKED_TOKENS: set[str] = set()


def _create_token(subject: str) -> str:
    expires_at = datetime.now(timezone.utc) + timedelta(seconds=TOKEN_TTL_SECONDS)
    return jwt.encode(
        {
            "sub": subject,
            "exp": expires_at,
            "jti": str(uuid4()),
        },
        SECRET_KEY,
        algorithm=ALGORITHM,
    )


def _decode_bearer_token(
    authorization_header: str | None,
) -> tuple[str | None, dict[str, object] | None]:
    if not authorization_header:
        return "No token provided", None
    if not authorization_header.startswith("Bearer "):
        return "Invalid token", None

    token = authorization_header.removeprefix("Bearer ").strip()
    if token in _REVOKED_TOKENS:
        return "Invalid token", None
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except jwt.ExpiredSignatureError:
        return "Token expired", None
    except jwt.InvalidTokenError:
        return "Invalid token", None
    return None, payload


def login(email: str, password: str) -> tuple[int, dict[str, object]]:
    if _USERS.get(email) != password:
        return 401, {"error": "Invalid credentials"}

    token = _create_token(email)
    return 200, {"token": token, "expiresIn": TOKEN_TTL_SECONDS}


def get_protected_resource(authorization_header: str | None) -> tuple[int, dict[str, str]]:
    error, _ = _decode_bearer_token(authorization_header)
    if error is not None:
        return 401, {"error": error}
    return 200, {"data": "protected resource"}


def refresh_token(authorization_header: str | None) -> tuple[int, dict[str, object]]:
    error, payload = _decode_bearer_token(authorization_header)
    if error is not None or payload is None:
        return 401, {"error": error or "Invalid token"}

    return 200, {
        "token": _create_token(str(payload["sub"])),
        "expiresIn": TOKEN_TTL_SECONDS,
    }


def logout(authorization_header: str | None) -> tuple[int, dict[str, str]]:
    error, _ = _decode_bearer_token(authorization_header)
    if error is not None:
        return 401, {"error": error}

    token = authorization_header.removeprefix("Bearer ").strip()
    _REVOKED_TOKENS.add(token)
    return 200, {"message": "Logged out"}
