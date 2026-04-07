from db.session import engine
from db.base import Base
from models.user import User
from models.portfolio import Portfolio


async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
