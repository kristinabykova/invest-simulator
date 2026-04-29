from decimal import Decimal
from types import SimpleNamespace
from unittest.mock import AsyncMock
from uuid import uuid4

import pytest
from fastapi import HTTPException

from src.services import portfolio


@pytest.fixture
def anyio_backend():
    return "asyncio"


@pytest.fixture
def fake_session():
    return SimpleNamespace(
        commit=AsyncMock(),
        rollback=AsyncMock(),
        refresh=AsyncMock(),
    )


@pytest.fixture
def fake_user():
    return SimpleNamespace(id=1)


@pytest.mark.anyio
async def test_buy_stock_success(monkeypatch, fake_session, fake_user):
    data = SimpleNamespace(ticker="SBER", qty=2)

    fake_portfolio = SimpleNamespace(
        id=uuid4(),
        cash_balance=Decimal("1000"),
    )

    fake_position = SimpleNamespace(
        ticker="SBER",
        quantity=2,
    )

    async def fake_get_current_stock(ticker):
        return {"offer": 150.25, "bid": 149.8}

    async def fake_get_portfolio_by_id(user_id, session):
        return fake_portfolio

    async def fake_upsert_position(position_data, session):
        assert position_data.portfolio_id == fake_portfolio.id
        assert position_data.ticker == "SBER"
        assert position_data.quantity == 2
        assert position_data.price == Decimal("150.25")
        return fake_position

    monkeypatch.setattr(portfolio, "get_current_stock", fake_get_current_stock)
    monkeypatch.setattr(portfolio, "get_portfolio_by_id", fake_get_portfolio_by_id)
    monkeypatch.setattr(portfolio, "upsert_position", fake_upsert_position)

    result = await portfolio.buy_stock(data, fake_user, fake_session)

    assert result["msg"] == "Покупка выполнена"
    assert result["ticker"] == "SBER"
    assert result["qty"] == 2
    assert result["price"] == 150.25
    assert result["total_cost"] == Decimal("300.50")
    assert result["cash_balance"] == Decimal("699.50")

    fake_session.commit.assert_awaited_once()
    assert fake_session.refresh.await_count == 2
    fake_session.rollback.assert_not_awaited()


@pytest.mark.anyio
async def test_buy_stock_raises_404_if_buy_unavailable(
    monkeypatch, fake_session, fake_user
):
    data = SimpleNamespace(ticker="SBER", qty=2)

    async def fake_get_current_stock(ticker):
        return {"offer": None, "bid": 149.8}

    monkeypatch.setattr(portfolio, "get_current_stock", fake_get_current_stock)

    with pytest.raises(HTTPException) as exc:
        await portfolio.buy_stock(data, fake_user, fake_session)

    assert exc.value.status_code == 404
    assert exc.value.detail == "Покупка временно недоступна"

    fake_session.commit.assert_not_awaited()
    fake_session.rollback.assert_not_awaited()


@pytest.mark.anyio
async def test_buy_stock_raises_404_if_portfolio_not_found(
    monkeypatch, fake_session, fake_user
):
    data = SimpleNamespace(ticker="SBER", qty=2)

    async def fake_get_current_stock(ticker):
        return {"offer": 150.25, "bid": 149.8}

    async def fake_get_portfolio_by_id(user_id, session):
        return None

    monkeypatch.setattr(portfolio, "get_current_stock", fake_get_current_stock)
    monkeypatch.setattr(portfolio, "get_portfolio_by_id", fake_get_portfolio_by_id)

    with pytest.raises(HTTPException) as exc:
        await portfolio.buy_stock(data, fake_user, fake_session)

    assert exc.value.status_code == 404
    assert exc.value.detail == "Портфель не найден"

    fake_session.commit.assert_not_awaited()
    fake_session.rollback.assert_awaited_once()


@pytest.mark.anyio
async def test_buy_stock_raises_400_if_not_enough_money(
    monkeypatch, fake_session, fake_user
):
    data = SimpleNamespace(ticker="SBER", qty=10)

    fake_portfolio = SimpleNamespace(
        id=uuid4(),
        cash_balance=Decimal("100"),
    )

    async def fake_get_current_stock(ticker):
        return {"offer": 150.25, "bid": 149.8}

    async def fake_get_portfolio_by_id(user_id, session):
        return fake_portfolio

    monkeypatch.setattr(portfolio, "get_current_stock", fake_get_current_stock)
    monkeypatch.setattr(portfolio, "get_portfolio_by_id", fake_get_portfolio_by_id)

    with pytest.raises(HTTPException) as exc:
        await portfolio.buy_stock(data, fake_user, fake_session)

    assert exc.value.status_code == 400
    assert exc.value.detail == "Недостаточно средств"

    fake_session.commit.assert_not_awaited()
    fake_session.rollback.assert_awaited_once()


@pytest.mark.anyio
async def test_sell_stock_success_partial_position(
    monkeypatch, fake_session, fake_user
):
    data = SimpleNamespace(ticker="SBER", qty=2)

    fake_portfolio = SimpleNamespace(
        id=uuid4(),
        cash_balance=Decimal("1000"),
    )

    fake_position = SimpleNamespace(
        ticker="SBER",
        quantity=5,
    )

    updated_position = SimpleNamespace(
        ticker="SBER",
        quantity=3,
    )

    async def fake_get_current_stock(ticker):
        return {"offer": 151.0, "bid": 150.25}

    async def fake_get_portfolio_by_id(user_id, session):
        return fake_portfolio

    async def fake_get_position(portfolio_id, ticker, session):
        return fake_position

    async def fake_update_delete_position(position, qty, session):
        assert position == fake_position
        assert qty == 2
        return updated_position

    monkeypatch.setattr(portfolio, "get_current_stock", fake_get_current_stock)
    monkeypatch.setattr(portfolio, "get_portfolio_by_id", fake_get_portfolio_by_id)
    monkeypatch.setattr(portfolio, "get_position", fake_get_position)
    monkeypatch.setattr(
        portfolio, "update_delete_position", fake_update_delete_position
    )

    result = await portfolio.sell_stock(data, fake_user, fake_session)

    assert result["msg"] == "Продажа выполнена"
    assert result["ticker"] == "SBER"
    assert result["qty"] == 3
    assert result["price"] == 150.25
    assert result["total_cost"] == Decimal("300.50")
    assert result["cash_balance"] == Decimal("1300.50")

    fake_session.commit.assert_awaited_once()
    assert fake_session.refresh.await_count == 2
    fake_session.rollback.assert_not_awaited()


@pytest.mark.anyio
async def test_sell_stock_success_all_position(monkeypatch, fake_session, fake_user):
    data = SimpleNamespace(ticker="SBER", qty=5)

    fake_portfolio = SimpleNamespace(
        id=uuid4(),
        cash_balance=Decimal("1000"),
    )

    fake_position = SimpleNamespace(
        ticker="SBER",
        quantity=5,
    )

    async def fake_get_current_stock(ticker):
        return {"offer": 151.0, "bid": 150.25}

    async def fake_get_portfolio_by_id(user_id, session):
        return fake_portfolio

    async def fake_get_position(portfolio_id, ticker, session):
        return fake_position

    async def fake_update_delete_position(position, qty, session):
        return None

    monkeypatch.setattr(portfolio, "get_current_stock", fake_get_current_stock)
    monkeypatch.setattr(portfolio, "get_portfolio_by_id", fake_get_portfolio_by_id)
    monkeypatch.setattr(portfolio, "get_position", fake_get_position)
    monkeypatch.setattr(
        portfolio, "update_delete_position", fake_update_delete_position
    )

    result = await portfolio.sell_stock(data, fake_user, fake_session)

    assert result["msg"] == "Проданы все лоты акции"
    assert result["cash_balance"] == "1751.25"

    fake_session.commit.assert_awaited_once()
    fake_session.refresh.assert_awaited_once_with(fake_portfolio)
    fake_session.rollback.assert_not_awaited()


@pytest.mark.anyio
async def test_sell_stock_raises_404_if_sell_unavailable(
    monkeypatch, fake_session, fake_user
):
    data = SimpleNamespace(ticker="SBER", qty=2)

    async def fake_get_current_stock(ticker):
        return {"offer": 151.0, "bid": None}

    monkeypatch.setattr(portfolio, "get_current_stock", fake_get_current_stock)

    with pytest.raises(HTTPException) as exc:
        await portfolio.sell_stock(data, fake_user, fake_session)

    assert exc.value.status_code == 404
    assert exc.value.detail == "Продажа временно недоступна"

    fake_session.commit.assert_not_awaited()
    fake_session.rollback.assert_not_awaited()


@pytest.mark.anyio
async def test_sell_stock_raises_404_if_portfolio_not_found(
    monkeypatch, fake_session, fake_user
):
    data = SimpleNamespace(ticker="SBER", qty=2)

    async def fake_get_current_stock(ticker):
        return {"offer": 151.0, "bid": 150.25}

    async def fake_get_portfolio_by_id(user_id, session):
        return None

    monkeypatch.setattr(portfolio, "get_current_stock", fake_get_current_stock)
    monkeypatch.setattr(portfolio, "get_portfolio_by_id", fake_get_portfolio_by_id)

    with pytest.raises(HTTPException) as exc:
        await portfolio.sell_stock(data, fake_user, fake_session)

    assert exc.value.status_code == 404
    assert exc.value.detail == "Записи с таким user_id не существует"

    fake_session.commit.assert_not_awaited()
    fake_session.rollback.assert_awaited_once()


@pytest.mark.anyio
async def test_sell_stock_raises_404_if_position_not_found(
    monkeypatch, fake_session, fake_user
):
    data = SimpleNamespace(ticker="SBER", qty=2)

    fake_portfolio = SimpleNamespace(
        id=uuid4(),
        cash_balance=Decimal("1000"),
    )

    async def fake_get_current_stock(ticker):
        return {"offer": 151.0, "bid": 150.25}

    async def fake_get_portfolio_by_id(user_id, session):
        return fake_portfolio

    async def fake_get_position(portfolio_id, ticker, session):
        return None

    monkeypatch.setattr(portfolio, "get_current_stock", fake_get_current_stock)
    monkeypatch.setattr(portfolio, "get_portfolio_by_id", fake_get_portfolio_by_id)
    monkeypatch.setattr(portfolio, "get_position", fake_get_position)

    with pytest.raises(HTTPException) as exc:
        await portfolio.sell_stock(data, fake_user, fake_session)

    assert exc.value.status_code == 404
    assert exc.value.detail == "Нет записи об этой акции"

    fake_session.commit.assert_not_awaited()
    fake_session.rollback.assert_awaited_once()


@pytest.mark.anyio
async def test_sell_stock_raises_400_if_not_enough_stocks(
    monkeypatch, fake_session, fake_user
):
    data = SimpleNamespace(ticker="SBER", qty=10)

    fake_portfolio = SimpleNamespace(
        id=uuid4(),
        cash_balance=Decimal("1000"),
    )

    fake_position = SimpleNamespace(
        ticker="SBER",
        quantity=5,
    )

    async def fake_get_current_stock(ticker):
        return {"offer": 151.0, "bid": 150.25}

    async def fake_get_portfolio_by_id(user_id, session):
        return fake_portfolio

    async def fake_get_position(portfolio_id, ticker, session):
        return fake_position

    monkeypatch.setattr(portfolio, "get_current_stock", fake_get_current_stock)
    monkeypatch.setattr(portfolio, "get_portfolio_by_id", fake_get_portfolio_by_id)
    monkeypatch.setattr(portfolio, "get_position", fake_get_position)

    with pytest.raises(HTTPException) as exc:
        await portfolio.sell_stock(data, fake_user, fake_session)

    assert exc.value.status_code == 400
    assert exc.value.detail == "Недостаточно акций для продажи"

    fake_session.commit.assert_not_awaited()
    fake_session.rollback.assert_awaited_once()
