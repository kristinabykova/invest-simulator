from decimal import Decimal
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models.portfolio import Portfolio


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
    return res.scalar_one()
