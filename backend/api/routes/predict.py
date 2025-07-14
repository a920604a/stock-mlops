from fastapi import APIRouter, HTTPException
from src.predict import Predictor
from api.schemas.predict_request import PredictRequest, PredictResponse
from datetime import datetime

router = APIRouter()


@router.post("/predict", response_model=PredictResponse)
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
        raise HTTPException(status_code=400, detail=str(e))
