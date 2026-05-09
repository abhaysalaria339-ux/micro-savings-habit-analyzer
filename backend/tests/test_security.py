from datetime import timedelta

from app.core.security import (
    create_access_token,
    decode_access_token,
    hash_password,
    verify_password,
)


def test_password_hashing_and_verification() -> None:
    hashed_password = hash_password("strong-password")

    assert hashed_password != "strong-password"
    assert verify_password("strong-password", hashed_password) is True
    assert verify_password("wrong-password", hashed_password) is False


def test_access_token_round_trip() -> None:
    token = create_access_token(
        subject="user-id-123",
        expires_delta=timedelta(minutes=5),
    )

    payload = decode_access_token(token)

    assert payload is not None
    assert payload["sub"] == "user-id-123"
