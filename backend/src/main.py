from contextlib import asynccontextmanager
import os
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.services.cache_services import close_redis
from src.services.moex import close_http_client
from src.db.init_db import init_db
from src.routers import main_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield
    await close_redis()
    await close_http_client()


app = FastAPI(title="Investment Simulator API", lifespan=lifespan)
app.include_router(main_router, prefix="/api")

FRONTEND_ORIGINS = os.getenv("FRONTEND_ORIGINS", "")
origins = [origin.strip() for origin in FRONTEND_ORIGINS.split(",") if origin.strip()]

if origins:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )


@app.get("/")
def root():
    return {"status": "ok"}


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000)
