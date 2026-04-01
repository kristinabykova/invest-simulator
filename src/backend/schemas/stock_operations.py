from decimal import Decimal
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field


class CurrentStocks(BaseModel):
    offer: Optional[float]
    bid: Optional[float]
    last: Optional[float]


class BuyStock(BaseModel):
    ticker: str
    qty: int = Field(ge=1)


class SellStock(BuyStock):
    pass


class PositionSchema(BaseModel):
    portfolio_id: UUID
    ticker: str
    quantity: int = Field(ge=1)
    price: Decimal
