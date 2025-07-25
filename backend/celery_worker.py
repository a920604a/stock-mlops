# celery_worker.py
import os

from celery import Celery
from celery_prometheus import add_prometheus_option  # 新增導入

redis_host = os.getenv("REDIS_HOST", "localhost")

celery_app = Celery(
    "tasks",
    broker=f"redis://{redis_host}:6379/0",  # Redis 為任務佇列中介
    backend=f"redis://{redis_host}:6379/1",  # 追蹤任務狀態用
    include=["tasks.train_model_task", "tasks.predict_tasks"],
)

# 確保 Celery Worker 發送事件
celery_app.conf.update(
    worker_send_task_events=True,
    task_send_sent_event=True,
)

# 添加 Prometheus 選項
add_prometheus_option(celery_app)
