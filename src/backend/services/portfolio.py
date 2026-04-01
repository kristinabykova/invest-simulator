from decimal import Decimal

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from schemas.stock_operations import BuyStock, PositionSchema, SellStock
from crud.portfolio import get_portfolio_by_id, upsert_position
from models.user import User
from services.moex import get_current_stock


async def buy_stock(data: BuyStock, current_user: User, session: AsyncSession):
    stock_data = get_current_stock(data.ticker)
    current_buy = stock_data["offer"]

    if current_buy is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Покупка временно недоступна",
        )

    portfolio = await get_portfolio_by_id(current_user.id, session)
    if portfolio is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Записи с таким user_id не существует",
        )

    total_cost = Decimal(str(current_buy)) * Decimal(data.qty)

    if total_cost > portfolio.cash_balance:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Недостаточно средств",
        )
    portfolio.cash_balance -= total_cost

    position = PositionSchema(
        portfolio_id=portfolio.id,
        ticker=data.ticker,
        quantity=data.qty,
        price=Decimal(current_buy),
    )

    res = await upsert_position(position, session)

    await session.commit()
    await session.refresh(portfolio)

    return {
        "msg": "Покупка выполнена",
        "ticker": res.ticker,
        "qty": res.quantity,
        "price": str(current_buy),
        "total_cost": str(total_cost),
        "cash_balance": portfolio.cash_balance,
    }
