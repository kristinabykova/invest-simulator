from types import SimpleNamespace
from uuid import uuid4

import pytest
from fastapi import HTTPException
from jwt import ExpiredSignatureError, InvalidTokenError

from src.auth import auth_service


@pytest.fixture
def anyio_backend():
    return "asyncio"


@pytest.fixture
def fake_session():
    return SimpleNamespace()


@pytest.mark.anyio
async def test_validate_auth_user_success(monkeypatch, fake_session):
    data = SimpleNamespace(email="user@example.com", password="correct_password")

    fake_user = SimpleNamespace(
        email="user@example.com",
        password_hash="hashed_password",
        is_active=True,
    )

    async def fake_get_user_by_email(session, email):
        return fake_user

    def fake_validate_password(password, hashed_password):
        return password == "correct_password" and hashed_password == "hashed_password"

    monkeypatch.setattr(auth_service, "get_user_by_email", fake_get_user_by_email)
    monkeypatch.setattr(auth_service, "validate_password", fake_validate_password)

    result = await auth_service.validate_auth_user(data, fake_session)

    assert result == fake_user


@pytest.mark.anyio
async def test_validate_auth_user_raises_401_if_user_not_found(
    monkeypatch, fake_session
):
    data = SimpleNamespace(email="user@example.com", password="password")

    async def fake_get_user_by_email(session, email):
        return None

    monkeypatch.setattr(auth_service, "get_user_by_email", fake_get_user_by_email)

    with pytest.raises(HTTPException) as exc:
        await auth_service.validate_auth_user(data, fake_session)

    assert exc.value.status_code == 401
    assert exc.value.detail == "Invalid email or password"


@pytest.mark.anyio
async def test_validate_auth_user_raises_401_if_password_is_wrong(
    monkeypatch, fake_session
):
    data = SimpleNamespace(email="user@example.com", password="wrong_password")

    fake_user = SimpleNamespace(
        email="user@example.com",
        password_hash="hashed_password",
        is_active=True,
    )

    async def fake_get_user_by_email(session, email):
        return fake_user

    def fake_validate_password(password, hashed_password):
        return False

    monkeypatch.setattr(auth_service, "get_user_by_email", fake_get_user_by_email)
    monkeypatch.setattr(auth_service, "validate_password", fake_validate_password)

    with pytest.raises(HTTPException) as exc:
        await auth_service.validate_auth_user(data, fake_session)

    assert exc.value.status_code == 401
    assert exc.value.detail == "Invalid email or password"


@pytest.mark.anyio
async def test_validate_auth_user_raises_403_if_user_inactive(
    monkeypatch, fake_session
):
    data = SimpleNamespace(email="user@example.com", password="correct_password")

    fake_user = SimpleNamespace(
        email="user@example.com",
        password_hash="hashed_password",
        is_active=False,
    )

    async def fake_get_user_by_email(session, email):
        return fake_user

    def fake_validate_password(password, hashed_password):
        return True

    monkeypatch.setattr(auth_service, "get_user_by_email", fake_get_user_by_email)
    monkeypatch.setattr(auth_service, "validate_password", fake_validate_password)

    with pytest.raises(HTTPException) as exc:
        await auth_service.validate_auth_user(data, fake_session)

    assert exc.value.status_code == 403
    assert exc.value.detail == "user inactive"


@pytest.mark.anyio
async def test_get_current_user_success(monkeypatch, fake_session):
    user_id = uuid4()

    fake_user = SimpleNamespace(
        id=user_id,
        is_active=True,
    )

    def fake_decode_jwt(token):
        return {"sub": str(user_id)}

    async def fake_get_user_by_id(session, user_uuid):
        assert user_uuid == user_id
        return fake_user

    monkeypatch.setattr(auth_service, "decode_jwt", fake_decode_jwt)
    monkeypatch.setattr(auth_service, "get_user_by_id", fake_get_user_by_id)

    result = await auth_service.get_current_user(
        access_token="valid_token",
        session=fake_session,
    )

    assert result == fake_user


@pytest.mark.anyio
async def test_get_current_user_raises_401_if_token_missing(fake_session):
    with pytest.raises(HTTPException) as exc:
        await auth_service.get_current_user(
            access_token=None,
            session=fake_session,
        )

    assert exc.value.status_code == 401
    assert exc.value.detail == "Not authenticated"


@pytest.mark.anyio
async def test_get_current_user_raises_401_if_token_expired(monkeypatch, fake_session):
    def fake_decode_jwt(token):
        raise ExpiredSignatureError

    monkeypatch.setattr(auth_service, "decode_jwt", fake_decode_jwt)

    with pytest.raises(HTTPException) as exc:
        await auth_service.get_current_user(
            access_token="expired_token",
            session=fake_session,
        )

    assert exc.value.status_code == 401
    assert exc.value.detail == "Token expired"


@pytest.mark.anyio
async def test_get_current_user_raises_401_if_token_invalid(monkeypatch, fake_session):
    def fake_decode_jwt(token):
        raise InvalidTokenError

    monkeypatch.setattr(auth_service, "decode_jwt", fake_decode_jwt)

    with pytest.raises(HTTPException) as exc:
        await auth_service.get_current_user(
            access_token="invalid_token",
            session=fake_session,
        )

    assert exc.value.status_code == 401
    assert exc.value.detail == "Invalid token"


@pytest.mark.anyio
async def test_get_current_user_raises_401_if_sub_missing(monkeypatch, fake_session):
    def fake_decode_jwt(token):
        return {"email": "user@example.com"}

    monkeypatch.setattr(auth_service, "decode_jwt", fake_decode_jwt)

    with pytest.raises(HTTPException) as exc:
        await auth_service.get_current_user(
            access_token="token_without_sub",
            session=fake_session,
        )

    assert exc.value.status_code == 401
    assert exc.value.detail == "Invalid token payload"


@pytest.mark.anyio
async def test_get_current_user_raises_401_if_sub_is_not_uuid(
    monkeypatch, fake_session
):
    def fake_decode_jwt(token):
        return {"sub": "not_uuid"}

    monkeypatch.setattr(auth_service, "decode_jwt", fake_decode_jwt)

    with pytest.raises(HTTPException) as exc:
        await auth_service.get_current_user(
            access_token="token_with_bad_sub",
            session=fake_session,
        )

    assert exc.value.status_code == 401
    assert exc.value.detail == "Invalid user id"


@pytest.mark.anyio
async def test_get_current_user_raises_401_if_user_not_found(monkeypatch, fake_session):
    user_id = uuid4()

    def fake_decode_jwt(token):
        return {"sub": str(user_id)}

    async def fake_get_user_by_id(session, user_uuid):
        return None

    monkeypatch.setattr(auth_service, "decode_jwt", fake_decode_jwt)
    monkeypatch.setattr(auth_service, "get_user_by_id", fake_get_user_by_id)

    with pytest.raises(HTTPException) as exc:
        await auth_service.get_current_user(
            access_token="valid_token",
            session=fake_session,
        )

    assert exc.value.status_code == 401
    assert exc.value.detail == "User not found"


@pytest.mark.anyio
async def test_get_current_user_raises_403_if_user_inactive(monkeypatch, fake_session):
    user_id = uuid4()

    fake_user = SimpleNamespace(
        id=user_id,
        is_active=False,
    )

    def fake_decode_jwt(token):
        return {"sub": str(user_id)}

    async def fake_get_user_by_id(session, user_uuid):
        return fake_user

    monkeypatch.setattr(auth_service, "decode_jwt", fake_decode_jwt)
    monkeypatch.setattr(auth_service, "get_user_by_id", fake_get_user_by_id)

    with pytest.raises(HTTPException) as exc:
        await auth_service.get_current_user(
            access_token="valid_token",
            session=fake_session,
        )

    assert exc.value.status_code == 403
    assert exc.value.detail == "User inactive"
