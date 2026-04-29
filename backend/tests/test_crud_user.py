from types import SimpleNamespace
from unittest.mock import AsyncMock, Mock
from uuid import uuid4

import pytest

from src.crud import user as user_crud


@pytest.fixture
def anyio_backend():
    return "asyncio"


@pytest.fixture
def fake_session():
    return SimpleNamespace(
        execute=AsyncMock(),
        add=Mock(),
        commit=AsyncMock(),
        refresh=AsyncMock(),
    )


@pytest.mark.anyio
async def test_get_user_by_email_returns_user(fake_session):
    fake_user = SimpleNamespace(
        email="user@example.com",
        password_hash="hashed_password",
    )

    fake_result = SimpleNamespace(scalar_one_or_none=Mock(return_value=fake_user))

    fake_session.execute.return_value = fake_result

    result = await user_crud.get_user_by_email(
        session=fake_session,
        email_user="user@example.com",
    )

    assert result == fake_user
    fake_session.execute.assert_awaited_once()
    fake_result.scalar_one_or_none.assert_called_once()


@pytest.mark.anyio
async def test_get_user_by_email_returns_none_if_user_not_found(fake_session):
    fake_result = SimpleNamespace(scalar_one_or_none=Mock(return_value=None))

    fake_session.execute.return_value = fake_result

    result = await user_crud.get_user_by_email(
        session=fake_session,
        email_user="missing@example.com",
    )

    assert result is None
    fake_session.execute.assert_awaited_once()
    fake_result.scalar_one_or_none.assert_called_once()


@pytest.mark.anyio
async def test_get_user_by_id_returns_user(fake_session):
    user_id = uuid4()

    fake_user = SimpleNamespace(
        id=user_id,
        email="user@example.com",
    )

    fake_result = SimpleNamespace(scalar_one_or_none=Mock(return_value=fake_user))

    fake_session.execute.return_value = fake_result

    result = await user_crud.get_user_by_id(
        session=fake_session,
        user_id=user_id,
    )

    assert result == fake_user
    fake_session.execute.assert_awaited_once()
    fake_result.scalar_one_or_none.assert_called_once()


@pytest.mark.anyio
async def test_get_user_by_id_returns_none_if_user_not_found(fake_session):
    user_id = uuid4()

    fake_result = SimpleNamespace(scalar_one_or_none=Mock(return_value=None))

    fake_session.execute.return_value = fake_result

    result = await user_crud.get_user_by_id(
        session=fake_session,
        user_id=user_id,
    )

    assert result is None
    fake_session.execute.assert_awaited_once()
    fake_result.scalar_one_or_none.assert_called_once()


@pytest.mark.anyio
async def test_create_user_creates_user_with_hashed_password(monkeypatch, fake_session):
    data = SimpleNamespace(
        email="user@example.com",
        password="plain_password",
    )

    def fake_hash_password(password):
        assert password == "plain_password"
        return b"hashed_password"

    monkeypatch.setattr(user_crud, "hash_password", fake_hash_password)

    result = await user_crud.create_user(
        session=fake_session,
        data=data,
    )

    assert result.email == "user@example.com"
    assert result.password_hash == "hashed_password"
    assert result.password_hash != "plain_password"

    fake_session.add.assert_called_once_with(result)
    fake_session.commit.assert_awaited_once()
    fake_session.refresh.assert_awaited_once_with(result)
