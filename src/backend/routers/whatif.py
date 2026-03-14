from fastapi import APIRouter
from schemas.whatif import WhatIfRequest
from services.explanation import all_explanations
from services.whatif import analyze_whatif
from services.insight import build_metrics_for_llm, generate_insights, test

router = APIRouter(prefix="/whatif", tags=["whatif"])

@router.post("/analyze")
def analyze(req: WhatIfRequest):

    result = analyze_whatif(req.ticker, req.from_, req.to, req.interval, req.lots_count)

    result["explanations"] = all_explanations(result)

    metrics = build_metrics_for_llm(result, req)
    
    result["ai_text"] = generate_insights(metrics).model_dump()

    #result["ai_text"] = test()

    return result
