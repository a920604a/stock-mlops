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


# Pydantic schema 定義
class PredictionResponse(BaseModel):
    ticker: str
    predicted_close: float
    predicted_at: datetime
    target_date: datetime
    model_metadata_id: int

    class Config:
        orm_mode = True
