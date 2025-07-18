# api/routes/predict.py

from fastapi import APIRouter, HTTPException
from src.inference.predict import Predictor
from api.schemas.predict_request import PredictRequest, PredictResponse
from datetime import datetime

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
def predict(request: PredictRequest):
    try:
        # 強制把 target_date 轉為 "日期 + 00:00:00" 格式
        target_date_clean = datetime.combine(request.target_date, datetime.min.time())
        print(f"target_date_clean {target_date_clean} {type(target_date_clean)}")

        predictor = Predictor(request.ticker, request.exchange)
        predicted_price, actual_close, msg = predictor.predict_next_close(
            target_date_clean
        )

        print(f"predicted_price {predicted_price} vs actual price {actual_close}")
        predict_success_total.inc()
        return PredictResponse(
            ticker=request.ticker,
            exchange=request.exchange,
            target_date=request.target_date,
            predicted_close=predicted_price,
            actual_close=actual_close,
            predicted_at=datetime.utcnow(),
            msg=msg,
        )
    except Exception as e:
        predict_failure_total.inc()
        raise HTTPException(status_code=400, detail=str(e))
