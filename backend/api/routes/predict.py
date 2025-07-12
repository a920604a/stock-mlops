from fastapi import APIRouter, HTTPException
from src.predict import Predictor
from api.schemas.predict_request import PredictRequest, PredictResponse
from datetime import datetime

router = APIRouter()


@router.post("/predict", response_model=PredictResponse)
def predict(request: PredictRequest):
    try:
        predictor = Predictor(request.ticker, request.exchange)
        predicted_price = predictor.predict_next_close(request.target_date)

        return PredictResponse(
            ticker=request.ticker,
            exchange=request.exchange,
            target_date=request.target_date,
            predicted_close=predicted_price,
            actual_close=None,  # 預設空值
            predicted_at=datetime.utcnow(),
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
