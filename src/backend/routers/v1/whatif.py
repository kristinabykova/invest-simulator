from fastapi import APIRouter
from schemas.whatif import WhatIfRequest
from services.explanation import all_explanations
from services.whatif import analyze_whatif
from llm.insights import build_metrics_for_llm, generate_insights, test

router = APIRouter(prefix="/whatif", tags=["whatif"])

@router.post("/analyze")
def analyze(req: WhatIfRequest):

    result = analyze_whatif(req.ticker, req.from_, req.to, req.interval, req.lots_count)

    result["explanations"] = all_explanations(result)

    return result

@router.post("/analyze/ai")
async def analyze_ai(req: WhatIfRequest):

    result = analyze_whatif(req.ticker, req.from_, req.to, req.interval, req.lots_count)

    metrics = build_metrics_for_llm(result, req)

    # try:
    #     result = await generate_insights(metrics)
    #     result = result.model_dump()
    # except Exception:
    #     result = None

    try:
        result = await test()
        result = result.model_dump()
    except Exception:
        result = None

    return result

    
