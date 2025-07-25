from datetime import datetime, timedelta

from src.inference.predict import Predictor


def batch_predict(ticker: str, exchange: str, days: int = 7):
    predictor = Predictor(ticker, exchange)
    today = datetime.utcnow()
    results = []
    for i in range(days):
        target_date = today + timedelta(days=i + 1)
        pred = predictor.predict_next_close(target_date)
        results.append(pred)
    return results
