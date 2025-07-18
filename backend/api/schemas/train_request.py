# api/schemas/train_request.py
from pydantic import BaseModel


class TrainRequest(BaseModel):
    model_id: int  # 或 str，依你的 model id 類型調整


class TrainResponse(BaseModel):
    # status: str
    task_id: str
