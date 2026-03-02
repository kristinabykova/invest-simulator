from pydantic import BaseModel, Field
from typing import List, Literal, Optional

class Term(BaseModel):
    term: str = Field(..., min_length=2, max_length=60)
    definition: str = Field(..., min_length=5, max_length=220)

class InsightsResponse(BaseModel):
    explanation: str = Field(..., min_length=10, max_length=450)
    tip: str = Field(..., min_length=5, max_length=200)
    terms: List[Term] = Field(default_factory=list, max_items=3)
    tone: Literal["нейтрально-обучающий"] = "нейтрально-обучающий"

class MetricsIn(BaseModel):
    ticker: str
    first_close: float
    last_close: float
    period_high: float
    period_low: float
    profit: float
    roi: float
    volatility_pct: float
    volatility_label: str           
    trend: str                
    risk: str                 
    lots: int
    comment: Optional[str] = None
