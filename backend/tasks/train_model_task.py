# tasks/train_model_task.py
from datetime import datetime
from celery_worker import celery_app
from src.model_training.train import train_ml_model
from src.train_config import TrainConfig
from src.db.postgres.models.models import ModelMetadata  # ORM 類別
import logging

logger = logging.getLogger(__name__)  # 建立 logger

from api.metrics import (
    train_success_total,
    train_failure_total,
)


@celery_app.task(queue="train_queue")
def train_model_task(model: dict):

    try:
        config = TrainConfig(
            model_type=model["model_type"],
            feature_columns=model["features"],
            val_size=model.get("val_size"),
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
