from fastapi import APIRouter, Depends, HTTPException, status
from crud import create_user, get_user_by_email
from schemas.user import UserLogin
from sqlalchemy.ext.asyncio import AsyncSession
from db.session import async_session_maker


async def get_session():
    async with async_session_maker() as session:
        yield session


auth_router = APIRouter(prefix="auth")

auth_router.post("/register")


async def register_user(data: UserLogin, session: AsyncSession = Depends(get_session)):
    exist = await get_user_by_email(session, data.email)
    if exist:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="User with email already exists",
        )
    return await create_user(session, data)
