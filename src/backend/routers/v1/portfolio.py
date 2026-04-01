from decimal import Decimal

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from auth.auth_service import get_current_user
from crud.portfolio import get_portfolio_by_id, get_positions_by_portfolio_id
from services.portfolio import buy_stock, sell_stock
from schemas.stock_operations import BuyStock, SellStock
from db.dependencies import get_session
from models.user import User

router = APIRouter(tags=["Portfolio"], prefix="/portfolio")


@router.post("/buy")
async def make_buy(
    data: BuyStock,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    res = await buy_stock(data, current_user, session)
    return res


@router.post("/sell")
async def make_sell(
    data: SellStock,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    res = await sell_stock(data, current_user, session)
    return res


@router.get("/tickers")
async def get_tickers(
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    portfolio = await get_portfolio_by_id(current_user.id, session)

    if portfolio is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Портфель не найден"
        )

    positions = await get_positions_by_portfolio_id(portfolio.id, session)

    return {
        "msg": "Список активов",
        "positions": [
            {
                "ticker": p.ticker,
                "qty": p.quantity,
                "avg_price": p.price,
            }
            for p in positions
        ],
        "cash_balance": str(portfolio.cash_balance),
    }
