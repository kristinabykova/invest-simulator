import json
from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest

from src.services import moex


@pytest.fixture
def anyio_backend():
    return "asyncio"


class FakeResponse:
    def __init__(self, data):
        self._data = data

    def raise_for_status(self):
        pass

    def json(self):
        return self._data


@pytest.mark.anyio
async def test_get_current_stock_returns_prices_from_tqbr_row(monkeypatch):
    fake_data = {
        "marketdata": {
            "columns": [
                "BOARDID",
                "OFFER",
                "BID",
                "LAST",
                "LCURRENTPRICE",
                "MARKETPRICE",
            ],
            "data": [
                ["TQTF", 10, 9, 9.5, None, None],
                ["TQBR", 101.5, 100.5, 101.0, 100.8, 100.7],
            ],
        }
    }

    async def fake_get(url, params=None):
        assert "SBER.json" in url
        return FakeResponse(fake_data)

    fake_client = SimpleNamespace(get=fake_get)
    monkeypatch.setattr(moex, "_http_client", fake_client)

    result = await moex.get_current_stock("SBER")

    assert result == {
        "offer": 101.5,
        "bid": 100.5,
        "last": 101.0,
    }


@pytest.mark.anyio
async def test_get_current_stock_uses_lcurrent_when_last_is_missing(monkeypatch):
    fake_data = {
        "marketdata": {
            "columns": [
                "BOARDID",
                "OFFER",
                "BID",
                "LAST",
                "LCURRENTPRICE",
                "MARKETPRICE",
            ],
            "data": [
                ["TQBR", None, None, None, 150.25, 149.9],
            ],
        }
    }

    async def fake_get(url, params=None):
        return FakeResponse(fake_data)

    monkeypatch.setattr(moex, "_http_client", SimpleNamespace(get=fake_get))

    result = await moex.get_current_stock("SBER")

    assert result["offer"] == 150.25
    assert result["bid"] == 150.25
    assert result["last"] == 150.25


@pytest.mark.anyio
async def test_get_current_stock_uses_marketprice_when_last_and_lcurrent_are_missing(
    monkeypatch,
):
    fake_data = {
        "marketdata": {
            "columns": [
                "BOARDID",
                "OFFER",
                "BID",
                "LAST",
                "LCURRENTPRICE",
                "MARKETPRICE",
            ],
            "data": [
                ["TQBR", None, None, None, None, 99.9],
            ],
        }
    }

    async def fake_get(url, params=None):
        return FakeResponse(fake_data)

    monkeypatch.setattr(moex, "_http_client", SimpleNamespace(get=fake_get))

    result = await moex.get_current_stock("SBER")

    assert result == {
        "offer": 99.9,
        "bid": 99.9,
        "last": 99.9,
    }


@pytest.mark.anyio
async def test_get_current_stock_returns_none_prices_if_tqbr_row_not_found(monkeypatch):
    fake_data = {
        "marketdata": {
            "columns": [
                "BOARDID",
                "OFFER",
                "BID",
                "LAST",
                "LCURRENTPRICE",
                "MARKETPRICE",
            ],
            "data": [
                ["TQTF", 101.5, 100.5, 101.0, None, None],
            ],
        }
    }

    async def fake_get(url, params=None):
        return FakeResponse(fake_data)

    monkeypatch.setattr(moex, "_http_client", SimpleNamespace(get=fake_get))

    result = await moex.get_current_stock("SBER")

    assert result == {
        "offer": None,
        "bid": None,
        "last": None,
    }


@pytest.mark.anyio
async def test_get_stock_candles_returns_mapped_candles(monkeypatch):
    fake_data = {
        "candles": {
            "columns": ["begin", "close", "high", "low", "volume"],
            "data": [
                ["2024-01-01 10:00:00", 100.0, 105.0, 95.0, 1000],
                ["2024-01-02 10:00:00", 110.0, 115.0, 108.0, 2000],
            ],
        }
    }

    async def fake_get(url, params=None):
        assert "SBER/candles.json" in url
        assert params == {
            "interval": 24,
            "from": "2024-01-01",
            "till": "2024-01-31",
        }
        return FakeResponse(fake_data)

    monkeypatch.setattr(moex, "_http_client", SimpleNamespace(get=fake_get))

    result = await moex.get_stock_candles(
        ticker="SBER",
        date_from="2024-01-01",
        date_to="2024-01-31",
        interval=24,
    )

    assert result == [
        {
            "date": "2024-01-01 10:00:00",
            "close": 100.0,
            "high": 105.0,
            "low": 95.0,
        },
        {
            "date": "2024-01-02 10:00:00",
            "close": 110.0,
            "high": 115.0,
            "low": 108.0,
        },
    ]


@pytest.mark.anyio
async def test_get_cache_stock_lotsize_returns_cached_value(monkeypatch):
    fake_redis = SimpleNamespace(
        get=AsyncMock(return_value="10"),
        setex=AsyncMock(),
    )

    monkeypatch.setattr(moex, "redis_client", fake_redis)

    result = await moex.get_cache_stock_lotsize("SBER")

    assert result == 10
    fake_redis.get.assert_awaited_once_with("stock_lotsize:SBER")
    fake_redis.setex.assert_not_awaited()


@pytest.mark.anyio
async def test_get_cache_stock_lotsize_fetches_from_moex_and_saves_to_cache(
    monkeypatch,
):
    fake_data = {
        "securities": {
            "columns": ["SECID", "LOTSIZE", "SHORTNAME"],
            "data": [
                ["SBER", 10, "Сбербанк"],
            ],
        }
    }

    fake_redis = SimpleNamespace(
        get=AsyncMock(return_value=None),
        setex=AsyncMock(),
    )

    async def fake_get(url, params=None):
        assert "SBER.json" in url
        assert params == {"iss.only": "securities"}
        return FakeResponse(fake_data)

    monkeypatch.setattr(moex, "redis_client", fake_redis)
    monkeypatch.setattr(moex, "_http_client", SimpleNamespace(get=fake_get))

    result = await moex.get_cache_stock_lotsize("SBER")

    assert result == 10
    fake_redis.get.assert_awaited_once_with("stock_lotsize:SBER")
    fake_redis.setex.assert_awaited_once_with("stock_lotsize:SBER", 600, 10)


@pytest.mark.anyio
async def test_get_cache_stock_lotsize_returns_none_if_no_info(monkeypatch):
    fake_data = {
        "securities": {
            "columns": ["SECID", "LOTSIZE"],
            "data": [],
        }
    }

    fake_redis = SimpleNamespace(
        get=AsyncMock(return_value=None),
        setex=AsyncMock(),
    )

    async def fake_get(url, params=None):
        return FakeResponse(fake_data)

    monkeypatch.setattr(moex, "redis_client", fake_redis)
    monkeypatch.setattr(moex, "_http_client", SimpleNamespace(get=fake_get))

    result = await moex.get_cache_stock_lotsize("SBER")

    assert result is None
    fake_redis.setex.assert_not_awaited()


@pytest.mark.anyio
async def test_get_cache_stock_candle_returns_cached_data(monkeypatch):
    cached_candles = [
        {
            "date": "2024-01-01",
            "close": 100,
            "high": 105,
            "low": 95,
        }
    ]

    fake_redis = SimpleNamespace(
        get=AsyncMock(return_value=json.dumps(cached_candles)),
        setex=AsyncMock(),
    )

    monkeypatch.setattr(moex, "redis_client", fake_redis)

    result = await moex.get_cache_stock_candle("SBER", 30)

    assert result == cached_candles
    fake_redis.get.assert_awaited_once_with("stock_history:SBER:30")
    fake_redis.setex.assert_not_awaited()


@pytest.mark.anyio
async def test_get_cache_stock_candle_fetches_and_saves_to_cache(monkeypatch):
    candles = [
        {
            "date": "2024-01-01",
            "close": 100,
            "high": 105,
            "low": 95,
        }
    ]

    fake_redis = SimpleNamespace(
        get=AsyncMock(return_value=None),
        setex=AsyncMock(),
    )

    async def fake_get_stock_candles(ticker, date_from, date_to):
        assert ticker == "SBER"
        return candles

    monkeypatch.setattr(moex, "redis_client", fake_redis)
    monkeypatch.setattr(moex, "get_stock_candles", fake_get_stock_candles)

    result = await moex.get_cache_stock_candle("SBER", 30)

    assert result == candles
    fake_redis.get.assert_awaited_once_with("stock_history:SBER:30")
    fake_redis.setex.assert_awaited_once_with(
        "stock_history:SBER:30",
        60,
        json.dumps(candles),
    )


@pytest.mark.anyio
async def test_close_http_client(monkeypatch):
    fake_client = SimpleNamespace(
        aclose=AsyncMock(),
    )

    monkeypatch.setattr(moex, "_http_client", fake_client)

    await moex.close_http_client()

    fake_client.aclose.assert_awaited_once()
