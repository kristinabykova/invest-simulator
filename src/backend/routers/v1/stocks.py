from fastapi import APIRouter, HTTPException, status
from services.moex import (
    get_cache_stock_lotsize,
    get_cache_stock_candle,
)
from services.stocks import list_of_stocks, is_supported_ticker
from schemas.whatif import Candle, LotSize

router = APIRouter(prefix="/stocks", tags=["Stocks"])


@router.get("/")
def get_stocks():
    return list_of_stocks()


@router.get("/{ticker}/lotsize", response_model=LotSize)
def get_lotsize(ticker: str) -> LotSize:
    if not is_supported_ticker(ticker):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "TICKER_NOT_FOUND", "msg": f"Unknown ticker: {ticker}"},
        )

    lotsize = get_cache_stock_lotsize(ticker)

    return {"ticker": ticker, "lotsize": lotsize}


@router.get("/{ticker}/history", response_model=list[Candle])
def stock_history(ticker: str, days: int = 3) -> list[Candle]:
    if not is_supported_ticker(ticker):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "TICKER_NOT_FOUND", "msg": f"Unknown ticker: {ticker}"},
        )
    result = get_cache_stock_candle(ticker, days)
    return result
