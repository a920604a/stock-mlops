# tasks/train_model_task.py
from datetime import datetime
from celery_worker import celery_app
from src.model_training.train import train_ml_model
from src.train_config import TrainConfig
from src.db.postgres.models.models import ModelMetadata  # ORM 類別
import logging

logger = logging.getLogger(__name__)  # 建立 logger

from prometheus_client import Counter, Histogram

train_success_total = Counter(
    "train_success_total", "Number of successful training jobs"
)
train_failure_total = Counter("train_failure_total", "Number of failed training jobs")
train_duration_seconds = Histogram(
    "train_duration_seconds", "Training duration in seconds"
)


@celery_app.task(bind=True)
def train_model_task(self, model: dict):
    try:
        config = TrainConfig(
            model_type=model["model_type"],
            feature_columns=model["features"],
            shuffle=model.get("shuffle"),
            n_estimators=100,
            train_end_date=model.get("train_end_date"),
            train_start_date=model.get("train_start_date"),
        )
        ticker = model.get("ticker")
        exchange = model.get("exchange")  # 如果有的話

        rmse, run_id = train_ml_model(model.get("id"), ticker, exchange, config)
        logger.info(f"訓練完成，rmse: {rmse}, run_id: {run_id}")
        train_success_total.inc()
        return {"status": "completed", "ticker": ticker, "rmse": rmse, "run_id": run_id}
    except Exception as e:
        train_failure_total.inc()
        return {"status": "failed", "error": str(e)}
