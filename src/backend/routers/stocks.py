from fastapi import APIRouter, HTTPException, status
from services.moex import get_stock_candles, get_stock_lotsize
from services.stocks import list_of_stocks, is_supported_ticker
from datetime import date, timedelta

router = APIRouter(prefix="/stocks", tags=["Stocks"])


@router.get("/")
def get_stocks():
    return list_of_stocks()

@router.get("/{ticker}/lotsize")
def get_lotsize(ticker: str):
    lotsize = get_stock_lotsize(ticker)

    if lotsize == None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "TICKER_NOT_FOUND", "msg": f"Unknown ticker: {ticker}"}
        )
    return {"ticker":ticker, "lotsize": lotsize}

@router.get("/{ticker}/history")
def stock_history(ticker: str, days: int = 3):
    if not is_supported_ticker(ticker):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "TICKER_NOT_FOUND", "msg": f"Unknown ticker: {ticker}"}
        )
    
    today = date.today()
    date_from = today - timedelta(days=days)
    return get_stock_candles(
        ticker=ticker,
        date_from=date_from.isoformat(),
        date_to=today.isoformat()
    )
