# backend/celery_worker.py
from celery import Celery
import os
redis_host = os.getenv("REDIS_HOST", "localhost")

celery_app = Celery(
    "tasks",
    broker=f"redis://{redis_host}:6379/0",  # Redis 為任務佇列中介
    backend=f"redis://{redis_host}:6379/1",  # 追蹤任務狀態用
)
