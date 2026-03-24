import uuid
from datetime import datetime

from sqlalchemy import DateTime, func, Uuid
from sqlalchemy.orm import Mapped, mapped_column

from db.base import Base, str_255


class User(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid,
        primary_key=True,
        server_default=func.gen_random_uuid(),
    )
    email: Mapped[str_255] = mapped_column(unique=True)
    password_hash: Mapped[str_255]
    is_active: Mapped[bool] = mapped_column(default=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )