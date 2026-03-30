import uuid

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from db.base import Base, pk, created_time, updated_time


class Portfolio(Base):
    __tablename__ = "portfolios"
    id: Mapped[pk]
    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE")
    )
    cash_balance: Mapped[float] = mapped_column(default=100000.00)
    created_at: Mapped[created_time]
    updated_at: Mapped[updated_time]
