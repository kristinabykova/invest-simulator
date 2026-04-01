from decimal import Decimal

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from auth.auth_service import get_current_user
from schemas.stock_operations import BuyStock
from db.dependencies import get_session
from models.user import User

router = APIRouter(tags=["Portfolio"], prefix="/portfolio")


@router.post("/buy")
async def make_buy(
    data: BuyStock,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    