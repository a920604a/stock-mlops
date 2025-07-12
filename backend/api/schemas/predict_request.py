from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class PredictRequest(BaseModel):
    ticker: str
    exchange: str
    target_date: datetime


class PredictResponse(BaseModel):
    ticker: str
    exchange: str
    target_date: datetime
    predicted_close: float
    actual_close: Optional[float] = None
    predicted_at: datetime
