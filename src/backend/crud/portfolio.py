from typing import List
from uuid import UUID
from sqlalchemy import and_, delete, select, update
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


async def get_portfolio_by_id(id_user: UUID, session: AsyncSession) -> Portfolio | None:
    query = select(Portfolio).where(Portfolio.user_id == id_user)
    res = await session.execute(query)
    res = res.scalar_one_or_none()
    return res


async def create_position(data: PositionSchema, session: AsyncSession) -> Position:
    position = Position(**data.model_dump())
    session.add(position)
    return position


async def upsert_position(data: PositionSchema, session: AsyncSession) -> Position:
    res = await get_position(data.portfolio_id, data.ticker, session)
    if res is None:
        return await create_position(data, session)

    avg_price = (res.quantity * res.price + data.quantity * data.price) / (
        res.quantity + data.quantity
    )
    res.quantity += data.quantity
    res.price = avg_price

    return res


async def get_positions_by_portfolio_id(
    p_id: UUID, session: AsyncSession
) -> List[Position]:
    query = select(Position).where(Position.portfolio_id == p_id)
    res = await session.execute(query)
    res = res.scalars().all()
    return res


async def get_position(
    p_id: UUID, ticker: str, session: AsyncSession
) -> Position | None:
    stmt = select(Position).where(
        and_(Position.portfolio_id == p_id, Position.ticker == ticker)
    )
    res = await session.execute(stmt)
    res = res.scalar_one_or_none()
    return res


async def update_delete_position(
    position: Position, qty: int, session: AsyncSession
) -> Position | None:
    if position.quantity == qty:
        await session.delete(position)
        return None
    position.quantity -= qty
    return position
