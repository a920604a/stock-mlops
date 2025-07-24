# api/routes/predict.py

from api.schemas.predict_request import FuturePredictResponse, FuturePredictRequest
from fastapi import APIRouter, HTTPException
from src.inference.predict import Predictor
from api.schemas.predict_request import (
    PredictRequest,
    PredictResponse,
    PredictionResponse,
)
from datetime import datetime, timedelta
from typing import List
from src.db.clickhouse.reader import read_predictions
from api.kafka_producer import send_prediction_to_kafka
import asyncio
import logging
import pandas as pd
from tasks.predict_tasks import simulate_future_predictions
from api.metrics import (
    predict_success_total,
    predict_failure_total,
)

from celery.result import AsyncResult
from celery_worker import celery_app


logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/predict/", response_model=PredictResponse)
async def create_prediction(request: PredictRequest):
    try:
        # 強制把 target_date 轉為 "日期 + 00:00:00" 格式
        target_date_clean = datetime.combine(request.target_date, datetime.min.time())
        print(f"target_date_clean {target_date_clean} {type(target_date_clean)}")

        predictor = Predictor(request.ticker, request.exchange)
        predicted_price, actual_close, msg, model_id = predictor.predict_next_close(
            target_date_clean
        )

        print(
            f"predicted_price {predicted_price} vs actual price {actual_close} at {request.target_date}"
        )
        predict_success_total.inc()

        prediction_result = {
            "ticker": request.ticker,
            "exchange": request.exchange,
            "target_date": request.target_date.isoformat(),
            "predicted_close": predicted_price,
            "actual_close": actual_close,
            "predicted_at": datetime.utcnow().isoformat(),
            "model_metadata_id": model_id,
            "msg": msg,
        }

        # **非同步觸發 Kafka 發送**
        asyncio.create_task(send_prediction_to_kafka(prediction_result))
        print(f"Prediction result sent to Kafka: {prediction_result}")

        return {"status": "submitted", "message": "預測任務已提交"}
    except Exception as e:
        predict_failure_total.inc()
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/predict/", response_model=List[PredictionResponse])
def list_predictions(ticker: str = None):

    df = read_predictions(ticker=ticker)
    if df is None or not isinstance(df, pd.DataFrame):
        # 如果不是 DataFrame，表示系統錯誤
        raise HTTPException(status_code=500, detail="預測資料讀取錯誤")

    # 如果沒有預測紀錄，直接回傳空陣列
    if df.empty:
        return []

    # 將 DataFrame 轉成 dict list，FastAPI 會自動轉換成 JSON
    results = df.to_dict(orient="records")
    return results


@router.post("/predict/future/", response_model=FuturePredictResponse)
async def create_future_predictions(req: FuturePredictRequest):

    print(f"Received future prediction request: {req}")
    task = simulate_future_predictions.delay(req.ticker, req.exchange, req.days)
    print(f"Future prediction task created: {task.id}")
    return FuturePredictResponse(status="submitted", task_id=task.id)


@router.get("/predict/future/status/{task_id}")
def get_future_prediction_status(task_id: str):
    # 這裡可以根據 task_id 查詢任務狀態
    result = AsyncResult(task_id, app=celery_app)
    logger.info(f"Checking status for future prediction task: {task_id}")
    if result.state == "PENDING":
        return {"task_id": task_id, "status": "pending"}
    elif result.state == "STARTED":
        return {"task_id": task_id, "status": "running"}
    elif result.state == "SUCCESS":
        return {"task_id": task_id, "status": "completed", "result": result.result}
    elif result.state == "FAILURE":
        return {"task_id": task_id, "status": "failed", "error": str(result.result)}
    else:
        raise HTTPException(status_code=400, detail="Unknown task state")
