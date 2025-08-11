# tasks/ingest_dataset_tasks.py
import json
import logging
import time
from datetime import datetime, timedelta
from workflows.etl_runner import trigger_etl_flow
from api.metrics import predict_failure_total, predict_success_total
from celery_worker import celery_app
from prometheus_client import Counter


logger = logging.getLogger(__name__)  # 建立 logger
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)


@celery_app.task(queue="dataset_ingestion")
def ingest_dataset(ticker_pairs):
    try:
        logger.info(f"開始處理 ETL 任務，股票清單: {ticker_pairs}")
        # 這邊呼叫原本的 ETL 流程函式
        trigger_etl_flow(ticker_pairs)  # 你要確保這函式可以被這裡 import
        logger.info("ETL 任務完成")
        return {"status": "success", "processed": len(ticker_pairs)}
    except Exception as e:
        logger.error(f"ETL 任務失敗: {str(e)}")
        return {"status": "failed", "error": str(e)}
    
    