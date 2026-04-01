from fastapi import APIRouter
from routers.v1.stocks import router as stocks_router
from routers.v1.analyze import router as analyze_router
from routers.v1.auth import router as auth_router
from routers.v1.portfolio import router as portfolio_router

main_router = APIRouter()

main_router.include_router(stocks_router)
main_router.include_router(analyze_router)
main_router.include_router(auth_router)
main_router.include_router(portfolio_router)
