import uuid

from sqlalchemy import 
from sqlalchemy.orm import Mapped, mapped_column

from db.base import Base, pk


class Portfolio(Base):
    __tablename__ = "portfolios"
    id: Mapped[pk]
