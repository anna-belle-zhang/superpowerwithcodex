from datetime import datetime, timedelta, timezone

import jwt

from src import jwt_auth


# Spec interpretation: the repo has no web framework, so the auth "routes"
# are represented as pure functions that return (status_code, payload).
def _make_token(*, subject: str = "user@example.com", expires_at: datetime) -> str:
    return jwt.encode(
        {"sub": subject, "exp": expires_at},
        jwt_auth.SECRET_KEY,
        algorithm=jwt_auth.ALGORITHM,
    )


def test_login_returns_jwt_and_expiry_for_valid_credentials() -> None:
    status_code, payload = jwt_auth.login("user@example.com", "correct-password")

    assert status_code == 200
    assert payload["expiresIn"] == 3600
    assert isinstance(payload["token"], str)
    assert payload["token"]

    decoded = jwt.decode(
        payload["token"],
        "development-secret",
        algorithms=["HS256"],
    )
    assert decoded["sub"] == "user@example.com"


def test_login_rejects_invalid_credentials() -> None:
    status_code, payload = jwt_auth.login("user@example.com", "wrong-password")

    assert status_code == 401
    assert payload == {"error": "Invalid credentials"}


def test_protected_route_allows_access_with_valid_bearer_token() -> None:
    _, login_payload = jwt_auth.login("user@example.com", "correct-password")

    status_code, payload = jwt_auth.get_protected_resource(
        f"Bearer {login_payload['token']}"
    )

    # Spec interpretation: "expected resource" is represented by a fixed payload
    # because the repo does not define an actual HTTP route handler.
    assert status_code == 200
    assert payload == {"data": "protected resource"}


def test_protected_route_rejects_missing_token() -> None:
    status_code, payload = jwt_auth.get_protected_resource(None)

    assert status_code == 401
    assert payload == {"error": "No token provided"}


def test_protected_route_rejects_expired_token() -> None:
    expired_token = _make_token(
        expires_at=datetime.now(timezone.utc) - timedelta(seconds=1)
    )

    status_code, payload = jwt_auth.get_protected_resource(f"Bearer {expired_token}")

    assert status_code == 401
    assert payload == {"error": "Token expired"}


def test_protected_route_rejects_malformed_token() -> None:
    _, login_payload = jwt_auth.login("user@example.com", "correct-password")
    malformed_token = f"{login_payload['token']}tampered"

    status_code, payload = jwt_auth.get_protected_resource(f"Bearer {malformed_token}")

    assert status_code == 401
    assert payload == {"error": "Invalid token"}


def test_refresh_returns_new_jwt_and_expiry_for_valid_token() -> None:
    _, login_payload = jwt_auth.login("user@example.com", "correct-password")

    status_code, payload = jwt_auth.refresh_token(f"Bearer {login_payload['token']}")

    assert status_code == 200
    assert payload["expiresIn"] == 3600
    assert payload["token"] != login_payload["token"]

    decoded = jwt.decode(
        payload["token"],
        jwt_auth.SECRET_KEY,
        algorithms=[jwt_auth.ALGORITHM],
    )
    assert decoded["sub"] == "user@example.com"


def test_logout_invalidates_token_for_future_requests() -> None:
    _, login_payload = jwt_auth.login("user@example.com", "correct-password")
    authorization_header = f"Bearer {login_payload['token']}"

    status_code, payload = jwt_auth.logout(authorization_header)

    assert status_code == 200
    assert payload == {"message": "Logged out"}

    follow_up_status, follow_up_payload = jwt_auth.get_protected_resource(
        authorization_header
    )

    # Spec interpretation: revoked tokens are rejected via the existing
    # "Invalid token" contract because no separate revoked-token payload exists.
    assert follow_up_status == 401
    assert follow_up_payload == {"error": "Invalid token"}
