from fastapi import APIRouter
from routers.stocks import router as stocks_router
from routers.whatif import router as whatif_router

main_router = APIRouter()

main_router.include_router(stocks_router)
main_router.include_router(whatif_router)