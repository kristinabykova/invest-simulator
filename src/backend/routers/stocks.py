from fastapi import APIRouter, HTTPException, status
from services.moex import get_stock_candles, get_stock_lotsize
from services.stocks import list_of_stocks, is_supported_ticker
from datetime import date, timedelta
from services.cache_services import redis_client
import json

router = APIRouter(prefix="/stocks", tags=["Stocks"])

@router.get("/")
def get_stocks():
    return list_of_stocks()

@router.get("/{ticker}/lotsize")
def get_lotsize(ticker: str):
    if not is_supported_ticker(ticker):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "TICKER_NOT_FOUND", "msg": f"Unknown ticker: {ticker}"}
        )
    lotsize = get_stock_lotsize(ticker)

    return {"ticker":ticker, "lotsize": lotsize}

@router.get("/{ticker}/history")
def stock_history(ticker: str, days: int = 3):
    if not is_supported_ticker(ticker):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "TICKER_NOT_FOUND", "msg": f"Unknown ticker: {ticker}"}
        )
    
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

