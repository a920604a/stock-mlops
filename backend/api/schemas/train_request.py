# backend/api/schemas/train_request.py
from pydantic import BaseModel
from typing import List
from datetime import datetime


class TrainRequest(BaseModel):
    ticker: str
    exchange: str
    model_type: str = "xgboost"
    n_estimators: int = 200
    shuffle: bool = True
    feature_columns: List[str]
    train_start_time: datetime
    train_end_time: datetime


class TrainResponse(BaseModel):
    status: str
    task_id: str
