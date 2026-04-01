import requests
import json
from datetime import date, timedelta

from schemas.stock_operations import CurrentStocks
from schemas.whatif import Candle
from services.cache_services import redis_client

MOEX_URL = "https://iss.moex.com/iss/engines/stock/markets/shares"


def get_current_stock(ticker: str) -> CurrentStocks:
    url = f"{MOEX_URL}/securities/{ticker}.json"
    response = requests.get(url)

    response.raise_for_status()
    data = response.json()

    columns = data["marketdata"]["columns"]
    rows = data["marketdata"]["data"]

    board_idx = columns.index("BOARDID")
    tqbr_row = None

    for row in rows:
        if row[board_idx] == "TQBR":
            tqbr_row = row
            break
    if not tqbr_row:
        return {"offer": None, "bid": None, "last": None}

    def get(field):
        return tqbr_row[columns.index(field)]

    offer = get("OFFER")
    bid = get("BID")
    last = get("LAST")
    lcurrent = get("LCURRENTPRICE")
    market = get("MARKETPRICE")

    price = last or lcurrent or market

    return {
        "offer": offer or price,
        "bid": bid or price,
        "last": price,
    }


def get_stock_candles(
    ticker: str, date_from: str, date_to: str, interval: int = 10
) -> list[Candle]:
    url = f"{MOEX_URL}/securities/{ticker}/candles.json"
    params = {"interval": interval, "from": date_from, "till": date_to}

    response = requests.get(url, params=params, timeout=5)
    response.raise_for_status()
    data = response.json()

    candles = data["candles"]["data"]
    columns = data["candles"]["columns"]

    result = []
    for candle in candles:
        item = dict(zip(columns, candle))
        result.append(
            {
                "date": item["begin"],
                "close": item["close"],
                "high": item["high"],
                "low": item["low"],
            }
        )

    return result


def get_stock_lotsize(ticker: str) -> None | int:

    url = f"{MOEX_URL}/securities/{ticker}.json"
    params = {"iss.only": "securities"}

    response = requests.get(url, params=params)
    response.raise_for_status()
    data = response.json()

    securities = data.get("securities", {})
    columns = securities.get("columns", [])
    info = securities.get("data", [])

    if info:
        d = dict(zip(columns, info[0]))
        return d["LOTSIZE"]
    return None


def get_cache_stock_candle(ticker: str, days: int):
    cache_key = f"stock_history:{ticker}:{days}"
    cached_data = redis_client.get(cache_key)
    if cached_data:
        return json.loads(cached_data)

    today = date.today()
    date_from = today - timedelta(days=days)
    result = get_stock_candles(
        ticker=ticker, date_from=date_from.isoformat(), date_to=today.isoformat()
    )

    redis_client.setex(cache_key, 60, json.dumps(result))

    return result
