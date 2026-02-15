from fastapi import APIRouter
from pydantic import BaseModel
from services.whatif import analyze_whatif

router = APIRouter(prefix="/whatif", tags=["whatif"])

class WhatIfRequest(BaseModel):
    ticker: str
    from_: str
    to: str
    interval: int = 10
    lots_count: int

@router.post("/analyze")
def analyze(req: WhatIfRequest):
    return analyze_whatif(req.ticker, req.from_, req.to, req.interval, req.lots_count)
