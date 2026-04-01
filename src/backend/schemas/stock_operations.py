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


class PositionSchema(BaseModel):
    position_id: UUID
    ticker: str
    quantity: int = Field(ge=1)
    avg_price: Decimal
