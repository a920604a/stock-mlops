# backend/celery_worker.py
from celery import Celery

celery_app = Celery(
    "tasks",
    broker="redis://redis:6379/0",  # Redis 為任務佇列中介
    backend="redis://redis:6379/0",  # 追蹤任務狀態用
)
