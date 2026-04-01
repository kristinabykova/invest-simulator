from typing import Optional
import uuid
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from db.base import Base, pk, created_time, updated_time

from decimal import Decimal
from sqlalchemy import Numeric


class Portfolio(Base):
    __tablename__ = "portfolios"
    id: Mapped[pk]
    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        unique=True,
    )
    cash_balance: Mapped[Decimal] = mapped_column(Numeric(15, 2), default=100000.00)
    created_at: Mapped[created_time]
    updated_at: Mapped[updated_time]

    user = relationship("User", back_populates="portfolio")


class Position(Base):
    __tablename__ = "positions"
    id: Mapped[pk]
    portfolio_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("portfolios.id", ondelete="CASCADE"), unique=False
    )
    ticker: Mapped[str]
    quantity: Mapped[Optional[int]]
    avg_price: Mapped[Optional[Decimal]] = mapped_column(Numeric(15, 2))
    updated_at: Mapped[updated_time]
