# api/routes/predict.py

from fastapi import APIRouter, HTTPException
from src.inference.predict import Predictor
from api.schemas.predict_request import (
    PredictRequest,
    PredictResponse,
    PredictionResponse,
)
from datetime import datetime
from typing import List
from src.db.clickhouse.reader import read_predictions
from api.kafka_producer import send_prediction_to_kafka
import asyncio
import logging
import pandas as pd


logger = logging.getLogger(__name__)

router = APIRouter()

from prometheus_client import Counter, Histogram

predict_success_total = Counter(
    "predict_success_total", "Number of successful predict jobs"
)
predict_failure_total = Counter(
    "predict_failure_total", "Number of failed predict jobs"
)
predict_duration_seconds = Histogram(
    "predict_duration_seconds", "Predicting duration in seconds"
)


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
