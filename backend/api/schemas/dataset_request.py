from pydantic import BaseModel


class DatasetInfo(BaseModel):
    ticker: str
    exchange: str
    start_date: str  # ISO date string
    end_date: str
    count: int
    parquet_ready: bool  # 是否已轉檔 (此處示意，實務可連接其他服務判斷)
