from decimal import Decimal
from uuid import UUID
from sqlalchemy import and_, select, update
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


async def get_portfolio_by_id(id_user: UUID, session: AsyncSession) -> Decimal | None:
    query = select(Portfolio).where(Portfolio.user_id == id_user)
    res = await session.execute(query)
    res = res.scalar_one_or_none()
    return res


async def create_position(data: PositionSchema, session: AsyncSession):
    position = Position(**data.model_dump())
    session.add(position)


async def upsert_position(data: PositionSchema, session: AsyncSession):
    query = select(Position).where(
        and_(
            Position.portfolio_id == data.portfolio_id,
            Position.ticker == data.ticker,
        )
    )
    res = await session.execute(query)
    res = res.scalar_one_or_none()
    if res is None:
        return create_position(data, session)

    avg_price = (res.quantity * res.price + data.quantity * data.price) / (
        res.quantity + data.quantity
    )
    res.quantity += data.quantity
    res.price = avg_price

    await session.commit()
    await session.refresh(res)
    return res
