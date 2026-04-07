from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.auth_service import get_current_user
from src.crud.portfolio import get_portfolio_by_id, get_positions_by_portfolio_id
from src.services.portfolio import buy_stock, sell_stock
from src.schemas.stock_operations import (
    BuyStock,
    ListOfPositions,
    ResultOperation,
    SellAll,
    SellStock,
)
from src.db.dependencies import get_session
from src.models.user import User

router = APIRouter(tags=["Portfolio"], prefix="/portfolio")


@router.post("/buy", response_model=ResultOperation)
async def make_buy(
    data: BuyStock,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> ResultOperation:
    res = await buy_stock(data, current_user, session)
    return res


@router.post("/sell", response_model=ResultOperation | SellAll)
async def make_sell(
    data: SellStock,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> ResultOperation | SellAll:
    res = await sell_stock(data, current_user, session)
    return res


@router.get("/tickers", response_model=ListOfPositions)
async def get_tickers(
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> ListOfPositions:
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
                "price": p.price,
            }
            for p in positions
        ],
        "cash_balance": portfolio.cash_balance,
    }
