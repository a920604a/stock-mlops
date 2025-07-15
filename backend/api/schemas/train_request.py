# api/schemas/train_request.py
from pydantic import BaseModel
from typing import List
from datetime import datetime
from src.train_config import TrainConfig


class TrainRequest(BaseModel):
    ticker: str
    exchange: str
    config: TrainConfig

    class Config:
        allow_population_by_field_name = True  # 讓你用內部欄位名稱存取


class TrainResponse(BaseModel):
    status: str
    task_id: str
