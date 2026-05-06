import pytest

from src.services import analyze


@pytest.fixture
def anyio_backend():
    return "asyncio"


def test_detect_trend_returns_none_for_short_list():
    assert analyze.detect_trend([100, 101, 102, 103]) is None


def test_detect_trend_uptrend():
    closes = [100, 102, 104, 106, 108, 110]

    result = analyze.detect_trend(closes)

    assert result == "восходящий тренд"


def test_detect_trend_downtrend():
    closes = [110, 108, 106, 104, 102, 100]

    result = analyze.detect_trend(closes)

    assert result == "нисходящий тренд"


def test_detect_trend_sideways():
    closes = [100, 100.01, 100, 100.01, 100]

    result = analyze.detect_trend(closes)

    assert result == "боковой тренд"


def test_historical_volatility_returns_none_for_less_than_two_prices():
    assert analyze.historical_volatility([100]) is None


def test_historical_volatility_returns_none_for_less_than_two_returns():
    assert analyze.historical_volatility([100, 110]) is None


def test_historical_volatility_returns_float_for_valid_prices():
    closes = [100, 105, 103, 108, 110]

    result = analyze.historical_volatility(closes)

    assert isinstance(result, float)
    assert result > 0


@pytest.mark.parametrize(
    "volatility, expected",
    [
        (None, None),
        (0.1, "низкая"),
        (0.5, "средняя"),
        (1.0, "средняя"),
        (1.5, "высокая"),
        (2.0, "высокая"),
    ],
)
def test_volatility_label(volatility, expected):
    assert analyze.volatility_label(volatility) == expected


def test_profit_returns_correct_value():
    result = analyze.profit(
        first=100,
        last=120,
        lot_size=10,
        lots_count=2,
    )

    assert result == 400


@pytest.mark.parametrize(
    "first, last, lot_size, lots_count",
    [
        (0, 120, 10, 2),
        (100, 0, 10, 2),
        (100, 120, 0, 2),
        (100, 120, 10, 0),
    ],
)
def test_profit_returns_none_if_required_value_is_missing(
    first,
    last,
    lot_size,
    lots_count,
):
    assert analyze.profit(first, last, lot_size, lots_count) is None


def test_roi_returns_correct_value():
    result = analyze.roi(first=100, last=120)

    assert result == 20


@pytest.mark.parametrize(
    "first, last",
    [
        (0, 120),
        (100, 0),
    ],
)
def test_roi_returns_none_if_required_value_is_missing(first, last):
    assert analyze.roi(first, last) is None


@pytest.mark.parametrize(
    "volatility, roi_value, expected",
    [
        (None, 10, None),
        (1.0, None, "умеренный риск"),
        (2.0, 0, "высокий риск"),
        (2.0, -5, "высокий риск"),
        (0.3, 10, "низкий риск"),
        (1.0, 10, "умеренный риск"),
        (0.7, -2, "умеренный риск"),
        (0.3, 11, "умеренный риск"),
        (0.3, -11, "умеренный риск"),
        (2.0, -11, "высокий риск"),
    ],
)
def test_risk_assessment(volatility, roi_value, expected):
    assert analyze.risk_assessment(volatility, roi_value) == expected


@pytest.mark.anyio
async def test_analyze_whatif_returns_expected_result(monkeypatch):
    async def fake_get_stock_candles(ticker, date_from, date_to, interval):
        return [
            {"close": 100, "high": 105, "low": 95},
            {"close": 105, "high": 110, "low": 100},
            {"close": 110, "high": 115, "low": 105},
            {"close": 115, "high": 120, "low": 110},
            {"close": 120, "high": 125, "low": 115},
        ]

    async def fake_get_cache_stock_lotsize(ticker):
        return 10

    monkeypatch.setattr(analyze, "get_stock_candles", fake_get_stock_candles)
    monkeypatch.setattr(
        analyze, "get_cache_stock_lotsize", fake_get_cache_stock_lotsize
    )

    result = await analyze.analyze_whatif(
        ticker="SBER",
        from_date="2024-01-01",
        to_date="2024-01-31",
        interval=24,
        lots_count=2,
    )

    assert result["first_close"] == 100
    assert result["last_close"] == 120
    assert result["period_high"] == 125
    assert result["period_low"] == 95
    assert result["trend"] == "восходящий тренд"
    assert result["roi"] == 20
    assert result["profit"] == 400
    assert result["volatility"] is not None
    assert result["vol_label"] in {"низкая", "средняя", "высокая"}
    assert result["risk"] in {"низкий риск", "умеренный риск", "высокий риск"}
