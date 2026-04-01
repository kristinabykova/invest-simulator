from decimal import Decimal

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from auth.auth_service import get_current_user
from schemas.whatif import BuyStock
from crud.portfolio import get_cash_balance, update_cash_balance
from db.dependencies import get_session
from models.user import User
from services.moex import get_current_stock

router = APIRouter(tags=["Portfolio"], prefix="/portfolio")


@router.post("/buy")
async def make_buy(
    data: BuyStock,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    stock_data = get_current_stock(data.ticker)
    current_buy = stock_data["offer"]

    if current_buy is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Покупка временно недоступна",
        )

    cash_balance = await get_cash_balance(current_user.id, session)
    if cash_balance is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Записи с таким user_id не существует",
        )

    total_cost = Decimal(str(current_buy)) * Decimal(data.qty)

    if total_cost > cash_balance:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Недостаточно средств",
        )
    cash_balance -= total_cost
    await update_cash_balance(current_user.id, cash_balance, session)
    return {
        "msg": "Покупка выполнена",
        "ticker": data.ticker,
        "qty": data.qty,
        "price": str(current_buy),
        "total_cost": str(total_cost),
        "cash_balance": str(cash_balance),
    }
