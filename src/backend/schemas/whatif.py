from typing import Optional

from pydantic import BaseModel, Field


class WhatIfRequest(BaseModel):
    ticker: str
    from_: str
    to: str
    interval: int = 10
    lots_count: int


class Candle(BaseModel):
    date: str
    close: float
    high: float
    low: float


class LotSize(BaseModel):
    ticker: str
    lotsize: int


class CurrentStocks(BaseModel):
    offer: Optional[float]
    bid: Optional[float]
    last: Optional[float]


class BuyStock(BaseModel):
    ticker: str
    qty: int = Field(ge=1)
