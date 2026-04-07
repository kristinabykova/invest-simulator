from decimal import Decimal

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from src.schemas.stock_operations import (
    BuyStock,
    PositionSchema,
    ResultOperation,
    SellAll,
    SellStock,
)
from src.crud.portfolio import (
    get_portfolio_by_id,
    get_position,
    update_delete_position,
    upsert_position,
)
from src.models.user import User
from src.services.moex import get_current_stock


async def buy_stock(
    data: BuyStock, current_user: User, session: AsyncSession
) -> ResultOperation:
    stock_data = await get_current_stock(data.ticker)
    current_buy = stock_data["offer"]

    if current_buy is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Покупка временно недоступна",
        )

    buy_price = Decimal(str(current_buy))
    total_cost = buy_price * Decimal(data.qty)

    try:
        portfolio = await get_portfolio_by_id(current_user.id, session)
        if portfolio is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Портфель не найден",
            )

        if total_cost > portfolio.cash_balance:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Недостаточно средств",
            )

        portfolio.cash_balance -= total_cost

        position_data = PositionSchema(
            portfolio_id=portfolio.id,
            ticker=data.ticker,
            quantity=data.qty,
            price=buy_price,
        )

        res = await upsert_position(position_data, session)

        await session.commit()
        await session.refresh(portfolio)
        await session.refresh(res)

        return {
            "msg": "Покупка выполнена",
            "ticker": res.ticker,
            "qty": res.quantity,
            "price": current_buy,
            "total_cost": total_cost,
            "cash_balance": portfolio.cash_balance,
        }
    except Exception:
        await session.rollback()
        raise


async def sell_stock(
    data: SellStock, current_user: User, session: AsyncSession
) -> ResultOperation | SellAll:
    stock_data = await get_current_stock(data.ticker)
    current_sell = stock_data["bid"]
    if current_sell is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Продажа временно недоступна"
        )

    total_cost = Decimal(str(current_sell)) * Decimal(data.qty)

    try:
        portfolio = await get_portfolio_by_id(current_user.id, session)
        if portfolio is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Записи с таким user_id не существует",
            )

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

        portfolio.cash_balance += total_cost

        res = await update_delete_position(position, data.qty, session)

        await session.commit()
        await session.refresh(portfolio)
        if res is not None:
            await session.refresh(res)

        if res is None:
            return {
                "msg": "Проданы все лоты акции",
                "cash_balance": str(portfolio.cash_balance),
            }

        return {
            "msg": "Продажа выполнена",
            "ticker": res.ticker,
            "qty": res.quantity,
            "price": current_sell,
            "total_cost": total_cost,
            "cash_balance": portfolio.cash_balance,
        }
    except Exception:
        await session.rollback()
        raise
