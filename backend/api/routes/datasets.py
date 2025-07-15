from fastapi import APIRouter, Query, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from src.db.clickhouse.base_clickhouse import client
import logging

router = APIRouter()


class DatasetInfo(BaseModel):
    ticker: str
    exchange: str
    start_date: str  # ISO date string
    end_date: str
    count: int
    parquet_ready: bool  # 是否已轉檔 (此處示意，實務可連接其他服務判斷)

@router.get("/datasets", response_model=List[DatasetInfo])
def get_datasets():
    try:
        # SQL 聚合查詢: 依 ticker, exchange 分組，取最小日期、最大日期、筆數
        sql = """
        SELECT
            ticker,
            exchange,
            toString(min(Date)) AS start_date,
            toString(max(Date)) AS end_date,
            count() AS count
        FROM stock_prices
        GROUP BY ticker, exchange
        ORDER BY ticker, exchange
        """

        result = client.execute(sql)

        datasets = []
        for row in result:
            ticker_val, exchange_val, start_date, end_date, count = row
            # parquet_ready 這裡示意，實際邏輯視需求調整
            parquet_ready = count > 0
            datasets.append(DatasetInfo(
                ticker=ticker_val,
                exchange=exchange_val,
                start_date=start_date,
                end_date=end_date,
                count=count,
                parquet_ready=parquet_ready
            ))

        return datasets

    except Exception as e:
        logging.error(f"Error querying datasets: {e}")
        raise HTTPException(status_code=500, detail="查詢資料集失敗")
