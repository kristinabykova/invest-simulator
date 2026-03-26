from typing import Optional

from pydantic import EmailStr
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from backend.schemas.user import UserRead
from models.user import User


async def get_user_by_email(
    session: AsyncSession, email_user: EmailStr
) -> Optional[UserRead]:
    query = select(User).where(User.email == email_user)
    result = await session.execute(query)
    return result.scalar_one_or_none()
