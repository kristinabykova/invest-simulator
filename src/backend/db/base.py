from typing import Annotated
import uuid

from sqlalchemy import String, func
from sqlalchemy.orm import DeclarativeBase, mapped_column


str_255 = Annotated[str, 255]
pk = Annotated[
    uuid.UUID, mapped_column(primary_key=True, server_default=func.get_random_uuid())
]


class Base(DeclarativeBase):
    type_annotation_map = {str_255: String(255)}
