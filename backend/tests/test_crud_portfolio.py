from decimal import Decimal
from types import SimpleNamespace
from unittest.mock import AsyncMock, Mock
from uuid import uuid4

import pytest

from src.crud import portfolio as portfolio_crud
from src.schemas.stock_operations import PositionSchema


@pytest.fixture
def anyio_backend():
    return "asyncio"


@pytest.fixture
def fake_session():
    return SimpleNamespace(
        add=Mock(),
        delete=AsyncMock(),
        commit=AsyncMock(),
        refresh=AsyncMock(),
    )


@pytest.mark.anyio
async def test_create_position_adds_position_to_session(fake_session):
    data = PositionSchema(
        portfolio_id=uuid4(),
        ticker="SBER",
        quantity=2,
        price=Decimal("150.25"),
    )

    result = await portfolio_crud.create_position(data, fake_session)

    assert result.portfolio_id == data.portfolio_id
    assert result.ticker == "SBER"
    assert result.quantity == 2
    assert result.price == Decimal("150.25")

    fake_session.add.assert_called_once_with(result)


@pytest.mark.anyio
async def test_upsert_position_creates_position_if_not_exists(
    monkeypatch, fake_session
):
    data = PositionSchema(
        portfolio_id=uuid4(),
        ticker="SBER",
        quantity=2,
        price=Decimal("150.25"),
    )

    async def fake_get_position(p_id, ticker, session):
        return None

    async def fake_create_position(position_data, session):
        return SimpleNamespace(
            portfolio_id=position_data.portfolio_id,
            ticker=position_data.ticker,
            quantity=position_data.quantity,
            price=position_data.price,
        )

    monkeypatch.setattr(portfolio_crud, "get_position", fake_get_position)
    monkeypatch.setattr(portfolio_crud, "create_position", fake_create_position)

    result = await portfolio_crud.upsert_position(data, fake_session)

    assert result.portfolio_id == data.portfolio_id
    assert result.ticker == "SBER"
    assert result.quantity == 2
    assert result.price == Decimal("150.25")


@pytest.mark.anyio
async def test_upsert_position_updates_existing_position(fake_session, monkeypatch):
    portfolio_id = uuid4()

    existing_position = SimpleNamespace(
        portfolio_id=portfolio_id,
        ticker="SBER",
        quantity=2,
        price=Decimal("100"),
    )

    data = PositionSchema(
        portfolio_id=portfolio_id,
        ticker="SBER",
        quantity=2,
        price=Decimal("200"),
    )

    async def fake_get_position(p_id, ticker, session):
        return existing_position

    monkeypatch.setattr(portfolio_crud, "get_position", fake_get_position)

    result = await portfolio_crud.upsert_position(data, fake_session)

    assert result == existing_position
    assert result.quantity == 4
    assert result.price == Decimal("150")


@pytest.mark.anyio
async def test_update_delete_position_deletes_position_if_quantity_equal(fake_session):
    position = SimpleNamespace(
        ticker="SBER",
        quantity=5,
    )

    result = await portfolio_crud.update_delete_position(
        position=position,
        qty=5,
        session=fake_session,
    )

    assert result is None
    fake_session.delete.assert_awaited_once_with(position)


@pytest.mark.anyio
async def test_update_delete_position_decreases_quantity_if_quantity_less(fake_session):
    position = SimpleNamespace(
        ticker="SBER",
        quantity=5,
    )

    result = await portfolio_crud.update_delete_position(
        position=position,
        qty=2,
        session=fake_session,
    )

    assert result == position
    assert position.quantity == 3
    fake_session.delete.assert_not_awaited()
