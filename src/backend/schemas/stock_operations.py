from typing import Optional

from pydantic import BaseModel, Field


class CurrentStocks(BaseModel):
    offer: Optional[float]
    bid: Optional[float]
    last: Optional[float]


class BuyStock(BaseModel):
    ticker: str
    qty: int = Field(ge=1)
