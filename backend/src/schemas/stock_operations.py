from decimal import Decimal
from typing import Any, List, Optional
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


class ResultOperation(BaseModel):
    msg: str
    ticker: str
    qty: int = Field(ge=1)
    price: Decimal = Field(example=150.25)
    total_cost: Decimal = Field(example=1502.50)
    cash_balance: Decimal = Field(example=98497.50)


class SellAll(BaseModel):
    msg: str
    cash_balance: Decimal = Field(example=98497.50)


class Pos(BaseModel):
    ticker: str
    qty: int = Field(ge=1)
    price: Decimal = Field(example=150.25)


class ListOfPositions(BaseModel):
    msg: str
    positions: List[Pos]
    cash_balance: Decimal = Field(example=100000.00)
