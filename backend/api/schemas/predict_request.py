from pydantic import BaseModel
from datetime import date, datetime
from typing import Optional


class PredictRequest(BaseModel):
    ticker: str
    exchange: str
    target_date: date


class PredictResponse(BaseModel):
    ticker: str
    exchange: str
    target_date: date
    predicted_close: float
    actual_close: Optional[float] = None
    predicted_at: datetime
    msg: str
