from decimal import Decimal
from uuid import UUID
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from schemas.stock_operations import PositionSchema
from models.portfolio import Portfolio, Position


async def create_portfolio(id: UUID, session: AsyncSession) -> Portfolio:
    portfolio = Portfolio()
    portfolio.user_id = id
    session.add(portfolio)
    await session.commit()
    await session.refresh(portfolio)
    return portfolio


async def get_cash_balance(id_user: UUID, session: AsyncSession) -> Decimal:
    query = select(Portfolio).where(Portfolio.user_id == id_user)
    res = await session.execute(query)
    res = res.scalar_one_or_none()
    if res is None:
        return None
    return res.cash_balance


async def update_cash_balance(id_user: UUID, cash: Decimal, session: AsyncSession):
    stmt = (
        update(Portfolio).where(Portfolio.user_id == id_user).values(cash_balance=cash)
    )
    await session.execute(stmt)
    await session.commit()


async def create_position(data: PositionSchema, session: AsyncSession):
    position = Position(**data.model_dump())
    session.add(position)
    await session.commit()
    await session.refresh(position)
