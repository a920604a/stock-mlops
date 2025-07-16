# api/routes/etl.py
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List
from workflows.etl_runner import trigger_etl_flow
from api.schemas.dataset_request import TickerExchange

router = APIRouter()


@router.post("/run-etl")
async def run_etl(tickers: List[TickerExchange]):
    try:
        # 將資料轉成 tuple 傳給 Flow
        ticker_pairs = [(item.ticker, item.exchange) for item in tickers]
        trigger_etl_flow(ticker_pairs)
        return {"message": "ETL 任務已觸發"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
