from pydantic import BaseModel


class TrainRequest(BaseModel):
    ticker: str
    exchange: str


class PredictRequest(BaseModel):
    MA10: float
