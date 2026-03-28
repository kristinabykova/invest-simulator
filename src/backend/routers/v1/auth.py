from fastapi import APIRouter, Depends, HTTPException, status
from auth.utils import validate_password, encode_jwt
from crud import create_user, get_user_by_email
from schemas.user import UserLogin, UserRead, Token
from sqlalchemy.ext.asyncio import AsyncSession
from db.session import async_session_maker


router = APIRouter(prefix="/auth", tags=["Auth"])


async def get_session():
    async with async_session_maker() as session:
        yield session


async def validate_auth_user(session: AsyncSession, data: UserLogin):
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
    return user


@router.post("/register", response_model=UserRead)
async def register_user(data: UserLogin, session: AsyncSession = Depends(get_session)):
    exist = await get_user_by_email(session, data.email)
    if exist:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="User with email already exists",
        )
    return await create_user(session, data)


@router.post("/login", response_model=Token)
async def login_user(
    data: UserLogin, session: AsyncSession = Depends(get_session)
) -> Token:
    user = await validate_auth_user(session, data)

    jwt_payload = {"sub": str(user.id)}
    token = encode_jwt(jwt_payload)

    return Token(access_token=token, token_type="Bearer")
