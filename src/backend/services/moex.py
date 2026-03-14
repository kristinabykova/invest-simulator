import requests
import json
from datetime import date, timedelta

from schemas.whatif import Candle
from services.cache_services import redis_client

MOEX_URL = "https://iss.moex.com/iss/engines/stock/markets/shares"

def get_stock_candles(ticker: str, date_from: str, date_to: str, 
                      interval: int=10) -> list[Candle]:
    url = f"{MOEX_URL}/securities/{ticker}/candles.json"
    params = {
        "interval": interval,  
        "from": date_from,
        "till": date_to
    }

    response = requests.get(url, params=params, timeout=5)
    data = response.json()

    candles = data["candles"]["data"]
    columns = data["candles"]["columns"]

    result = []
    for candle in candles:
        item = dict(zip(columns, candle))
        result.append({
            "date": item["begin"],
            "close": item["close"],
            "high": item["high"],
            "low": item["low"]
        })

    return result

def get_stock_lotsize(ticker:str) -> None | int:

    url = f"{MOEX_URL}/securities/{ticker}.json"
    params = {"iss.only":"securities"}

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
        ticker=ticker,
        date_from=date_from.isoformat(),
        date_to=today.isoformat()
    )

    redis_client.setex(
        cache_key,
        60,  
        json.dumps(result)
    )

    return result

    




