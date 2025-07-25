# tasks/predict_tasks.py
import json
import logging
import time
from datetime import datetime, timedelta

from api.metrics import predict_failure_total, predict_success_total
from celery_worker import celery_app
from prometheus_client import Counter
from src.inference.predict import Predictor
from src.utils.redis import redis_client  # 假設這是你的 redis client

logger = logging.getLogger(__name__)  # 建立 logger
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)


@celery_app.task(queue="predict_queue")
def simulate_future_predictions(ticker: str, exchange: str, days: int = 3):
    """
    模擬每天預測一次，持續 days 天
    """
    try:
        logger.info(f"開始模擬未來 {days} 天的預測，股票: {ticker}, 交易所: {exchange}")
        task_id = simulate_future_predictions.request.id  # 取得該任務的 ID

        predictor = Predictor(ticker, exchange)
        start_dt = datetime.now() + timedelta(days=1)

        predictions = []
        for i in range(days):
            target_date = start_dt + timedelta(days=i)
            pred = predictor.predict_next_close(target_date)

            if pred is None:
                continue

            predicted_price, actual_close, msg, model_id = pred
            predictions.append(
                {
                    "target_date": target_date.date().isoformat(),
                    "predicted_close": predicted_price,
                    "actual_close": actual_close,
                    "model_metadata_id": model_id,
                    "msg": msg,
                }
            )

            predict_success_total.inc()
            # 模擬每天執行一次
            if i < days - 1:
                # time.sleep(24 * 60 * 60)  # 等待一天
                time.sleep(3)  # 等待1分鐘

            # 🔁 每次都把目前累積結果寫進 Redis

            redis_client.set(f"future_predict:{task_id}", json.dumps(predictions))
            logger.info(f"redis_client set: {predictions} {len(predictions)} 天")

        logger.info(f"模擬預測完成，共 {len(predictions)} 天的預測結果")
        return {"status": "success", "predictions": predictions}

    except Exception as e:
        predict_failure_total.inc()
        logger.warning(f"模擬預測失敗: {str(e)}")
        return {"status": "failed", "error": str(e)}
