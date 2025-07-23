from pydantic import BaseModel
from datetime import date, datetime
from typing import Optional


class PredictRequest(BaseModel):
    ticker: str
    exchange: str
    target_date: date


class PredictResponse(BaseModel):
    status: str
    message: str


# Pydantic schema 定義
class PredictionResponse(BaseModel):
    ticker: str
    predicted_close: float
    predicted_at: datetime
    target_date: date
    model_metadata_id: int

    class Config:
        orm_mode = True
