# backend/tasks/train_model_task.py
from datetime import datetime
from celery_worker import celery_app
from src.train import train_and_register
from src.train_config import TrainConfig


@celery_app.task(bind=True)
def train_model_task(self, ticker: str, exchange: str, config_dict: dict):
    try:
        config = TrainConfig(**config_dict)
        print(f"ticker {ticker}")
        print(f"exchange {exchange}")
        print(f"config {config}")
        rmse, run_id = train_and_register(ticker, exchange, config)
        return {"status": "completed", "ticker": ticker, "rmse": rmse, "run_id": run_id}
    except Exception as e:
        return {"status": "failed", "error": str(e)}
