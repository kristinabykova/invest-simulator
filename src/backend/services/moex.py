import requests
from schemas.whatif import Candle

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



    

    




