# backend/api/schemas/train_request.py
from pydantic import BaseModel
from typing import List
from datetime import datetime
from src.train_config import TrainConfig

class TrainRequest(BaseModel):
    ticker: str
    exchange: str
    config: TrainConfig

class TrainResponse(BaseModel):
    status: str
    task_id: str
