from datetime import timedelta

import jwt
import pytest

from src.auth import utils

TEST_SECRET = "test-secret-key-minimum-32-bytes-long"
CORRECT_SECRET = "correct-secret-key-minimum-32-bytes-long"
WRONG_SECRET = "wrong-secret-key-minimum-32-bytes-long"


def test_hash_password_returns_bytes():
    hashed = utils.hash_password("password123")

    assert isinstance(hashed, bytes)
    assert hashed != b"password123"


def test_validate_password_returns_true_for_correct_password():
    hashed = utils.hash_password("password123").decode()

    result = utils.validate_password("password123", hashed)

    assert result is True


def test_validate_password_returns_false_for_wrong_password():
    hashed = utils.hash_password("password123").decode()

    result = utils.validate_password("wrong_password", hashed)

    assert result is False


def test_encode_jwt_returns_string_token():
    token = utils.encode_jwt(
        payload={"sub": "user@example.com"},
        key=TEST_SECRET,
        algorithm="HS256",
        expire_minutes=30,
    )

    assert isinstance(token, str)


def test_decode_jwt_returns_original_payload():
    token = utils.encode_jwt(
        payload={"sub": "user@example.com", "user_id": "123"},
        key=TEST_SECRET,
        algorithm="HS256",
        expire_minutes=30,
    )

    decoded = utils.decode_jwt(
        token=token,
        key=TEST_SECRET,
        algorithm="HS256",
    )

    assert decoded["sub"] == "user@example.com"
    assert decoded["user_id"] == "123"
    assert "exp" in decoded
    assert "iat" in decoded


def test_decode_jwt_raises_error_for_invalid_token():
    with pytest.raises(jwt.InvalidTokenError):
        utils.decode_jwt(
            token="invalid.token.value",
            key=TEST_SECRET,
            algorithm="HS256",
        )


def test_decode_jwt_raises_error_for_expired_token():
    token = utils.encode_jwt(
        payload={"sub": "user@example.com"},
        key=TEST_SECRET,
        algorithm="HS256",
        expire_delta=timedelta(seconds=-1),
    )

    with pytest.raises(jwt.ExpiredSignatureError):
        utils.decode_jwt(
            token=token,
            key=TEST_SECRET,
            algorithm="HS256",
        )


def test_decode_jwt_raises_error_for_wrong_secret_key():
    token = utils.encode_jwt(
        payload={"sub": "user@example.com"},
        key=CORRECT_SECRET,
        algorithm="HS256",
        expire_minutes=30,
    )

    with pytest.raises(jwt.InvalidSignatureError):
        utils.decode_jwt(
            token=token,
            key=WRONG_SECRET,
            algorithm="HS256",
        )
