import uuid

from fastapi import Depends, HTTPException, status, Cookie
from jwt import ExpiredSignatureError, InvalidTokenError
from sqlalchemy.ext.asyncio import AsyncSession

from auth.utils import validate_password
from crud.portfolio import create_portfolio
from db.dependencies import get_session
from crud.user import get_user_by_email, get_user_by_id
from schemas.user import UserLogin
from auth.utils import decode_jwt, validate_password


async def validate_auth_user(
    data: UserLogin, session: AsyncSession = Depends(get_session)
):
    unauthed_ex = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password"
    )
    user = await get_user_by_email(session, data.email)
    if not user:
        raise unauthed_ex
    pwd = data.password
    pwd_hash = user.password_hash
    val = validate_password(pwd, pwd_hash)
    if not val:
        raise unauthed_ex

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="user inactive",
        )

    res = await create_portfolio(user.id, session)
    print(res.id, res.user_id, res.cash_balance, res.created_at, res.updated_at)

    return user


async def get_current_user(
    access_token: str | None = Cookie(None),
    session: AsyncSession = Depends(get_session),
):
    if access_token is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
        )

    try:
        payload = decode_jwt(access_token)
    except ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token expired",
        )
    except InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
        )

    user_id = payload.get("sub")
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload",
        )

    try:
        user_uuid = uuid.UUID(user_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid user id",
        )

    user = await get_user_by_id(session, user_uuid)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User inactive",
        )

    return user
