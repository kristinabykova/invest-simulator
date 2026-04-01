from fastapi import APIRouter, Depends, HTTPException, status, Response
from auth.utils import encode_jwt
from auth.auth_service import get_current_user, validate_auth_user
from db.dependencies import get_session
from models.user import User
from crud.user import create_user, get_user_by_email
from schemas.user import UserLogin, UserRead, Token
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(prefix="/auth", tags=["Auth"])


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
    response: Response,
    data: UserLogin,
    session: AsyncSession = Depends(get_session),
) -> Token:
    user = await validate_auth_user(data, session)

    jwt_payload = {"sub": str(user.id)}
    token = encode_jwt(jwt_payload)
    response.set_cookie(
        key="access_token",
        value=token,
        httponly=True,
    )

    return Token(access_token=token, token_type="Bearer")


@router.get("/me", response_model=UserRead)
async def get_me(current_user: User = Depends(get_current_user)):
    return current_user


@router.post("/logout")
async def logout_user(response: Response):
    response.delete_cookie(key="access_token")
    return {"message": "Logged out"}
