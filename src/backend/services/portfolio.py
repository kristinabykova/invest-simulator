from decimal import Decimal

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from schemas.stock_operations import (
    BuyStock,
    PositionSchema,
    ResultOperation,
    SellAll,
    SellStock,
)
from crud.portfolio import (
    get_portfolio_by_id,
    get_position,
    update_delete_position,
    upsert_position,
)
from models.user import User
from services.moex import get_current_stock


async def buy_stock(
    data: BuyStock, current_user: User, session: AsyncSession
) -> ResultOperation:
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
        "cash_balance": str(portfolio.cash_balance),
    }


async def sell_stock(
    data: SellStock, current_user: User, session: AsyncSession
) -> ResultOperation | SellAll:
    stock_data = get_current_stock(data.ticker)
    current_sell = stock_data["bid"]
    if current_sell is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Продажа временно недоступна"
        )
    total_cost = Decimal(str(current_sell)) * Decimal(data.qty)

    portfolio = await get_portfolio_by_id(current_user.id, session)
    if portfolio is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Записи с таким user_id не существует",
        )

    portfolio.cash_balance += total_cost

    position = await get_position(portfolio.id, data.ticker, session)

    if position is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Нет записи об этой акции"
        )

    if data.qty > position.quantity:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Недостаточно акций для продажи",
        )

    res = await update_delete_position(position, data.qty, session)

    await session.commit()
    await session.refresh(portfolio)

    if res is None:
        return {
            "msg": "Проданы все лоты акции",
            "cash_balance": str(portfolio.cash_balance),
        }

    return {
        "msg": "Продажа выполнена",
        "ticker": res.ticker,
        "qty": res.quantity,
        "price": str(current_sell),
        "total_cost": str(total_cost),
        "cash_balance": str(portfolio.cash_balance),
    }
