from pydantic import BaseModel

class WhatIfRequest(BaseModel):
    ticker: str
    from_: str
    to: str
    interval: int = 10
    lots_count: int