import os
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.db.init_db import init_db
from src.routers import main_router

app = FastAPI(title="Investment Simulator API")
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


@app.on_event("startup")
async def startup():
    await init_db()


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000)
