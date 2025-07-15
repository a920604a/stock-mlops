# tasks/train_model_task.py
from datetime import datetime
from celery_worker import celery_app
from src.model_training.train import train_and_register
from src.train_config import TrainConfig

from prometheus_client import Counter, Histogram

train_success_total = Counter(
    "train_success_total", "Number of successful training jobs"
)
train_failure_total = Counter("train_failure_total", "Number of failed training jobs")
train_duration_seconds = Histogram(
    "train_duration_seconds", "Training duration in seconds"
)


@celery_app.task(bind=True)
def train_model_task(self, ticker: str, exchange: str, config_dict: dict):
    try:
        config = TrainConfig(**config_dict)
        print(f"ticker {ticker}")
        print(f"exchange {exchange}")
        print(f"config {config}")
        rmse, run_id = train_and_register(ticker, exchange, config)
        train_success_total.inc()
        return {"status": "completed", "ticker": ticker, "rmse": rmse, "run_id": run_id}
    except Exception as e:
        train_failure_total.inc()
        return {"status": "failed", "error": str(e)}
