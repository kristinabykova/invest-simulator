from services.moex import get_stock_candles, get_stock_lotsize
import math
import statistics

def detect_trend(closes, threshold_pct_per_step=0.01):
    if len(closes) < 5:
        return None

    n = len(closes)

    sum_x = sum(range(n))
    sum_y = sum(closes)
    sum_xx = sum(i * i for i in range(n))
    sum_xy = sum(i * closes[i] for i in range(n))

    denom = n * sum_xx - sum_x * sum_x
    if denom == 0:
        return "боковой тренд"

    slope = (n * sum_xy - sum_x * sum_y) / denom

    avg_price = sum_y / n
    slope_pct_per_step = (slope / avg_price) * 100

    if slope_pct_per_step > threshold_pct_per_step:
        return "восходящий тренд"
    
    elif slope_pct_per_step < -threshold_pct_per_step:
        return "нисходящий тренд"
    
    else:
        return "боковой тренд"

def historical_volatility(closes):
    if len(closes) < 2:
        return None

    returns = [
        math.log(closes[i] / closes[i - 1])
        for i in range(1, len(closes))
        if closes[i - 1] > 0
    ]

    if len(returns) < 2:
        return None

    return statistics.stdev(returns)

def profit(first: float, last: float, lot_size: int, lots_count: int):
    profit = None
    if lots_count and first and last and lot_size:
        profit = (last - first) * lot_size * lots_count
    return profit

def roi(first: float, last: float):
    roi = None
    if first and last:
        roi = (last - first) / first * 100
    return roi

def risk_assessment(volatility: float | None, roi: float | None) -> str | None:
    if volatility is None or roi is None:
        return None

    if volatility > 1.5 and roi <= 0:
        return "высокий риск"

    if volatility < 0.5 and roi > 0:
        return "низкий риск"

    return "умеренный риск"

def analyze_whatif(ticker: str, from_date: str, to_date: str, interval: int, lots_count: int):
    
    candles = get_stock_candles(
        ticker=ticker,
        date_from=from_date,
        date_to=to_date,
        interval=interval
    )
    
    lot_size = get_stock_lotsize(ticker)

    closes = [c["close"] for c in candles]

    first_close = candles[0]['close']
    last_close = candles[-1]['close']

    period_high = max(c["high"] for c in candles)
    period_low = min(c["low"] for c in candles)
    
    vol_raw = historical_volatility(closes)
    vol = None if vol_raw is None else vol_raw * 100

    trend = detect_trend(closes)

    profit_period = profit(first_close, last_close, lot_size, lots_count)

    roi_period = roi(first_close, last_close)

    risk = risk_assessment(vol, roi_period)

    return {

        "first_close": first_close,
        "last_close": last_close,
        "period_high": period_high,
        "period_low": period_low,
        "volatility": vol,
        "trend": trend,
        "roi": roi_period,
        "profit": profit_period,
        "risk": risk
    }