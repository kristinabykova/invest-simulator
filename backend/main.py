from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers.stocks import router as stocks_router
from routers.whatif import router as whatif_router
import uvicorn

app = FastAPI(title="Investment Simulator API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(stocks_router)
app.include_router(whatif_router)

@app.get("/")
def root():
    return {"status": "ok"}

if __name__ == "__main__":
    uvicorn.run("main:app", reload=True)
