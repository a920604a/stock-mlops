# api/routes/etl.py
from typing import List

from api.schemas.dataset_request import TickerExchange
from fastapi import APIRouter, HTTPException
from workflows.etl_runner import trigger_etl_flow

router = APIRouter()


@router.post("/run-etl")
async def run_etl(tickers: List[TickerExchange]):
    try:
        # 將資料轉成 tuple 傳給 Flow
        ticker_pairs = [(item.ticker, item.exchange) for item in tickers]
        print(f"run_etl ticker_pairs {ticker_pairs}")
        # trigger_etl_flow(ticker_pairs) // TODO: fixed
        # return {"message": f"成功觸發 ETL 任務，處理 {len(ticker_pairs)} 組股票資料"}
        return {"message": "目前還沒實做 請聯絡專員幫忙處理"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"ETL 執行錯誤: {str(e)}")
