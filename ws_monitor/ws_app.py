import asyncio
import logging

from create_clickhouse_table import create_clickhouse_table
from fastapi import FastAPI
from kafka_metrics_consumer import kafka_metrics_consumer_loop
from kafka_predictions_consumer import kafka_predictions_consumer_loop
from websocket_anomalies import websocket_alerts_endpoint
from websocket_metrics import websocket_metrics_endpoint
from websocket_predictions import websocket_predictions_endpoint

app = FastAPI()
logger = logging.getLogger(__name__)

# WebSocket 路由註冊
app.websocket("/ws/predictions")(websocket_predictions_endpoint)
app.websocket("/ws/metrics")(websocket_metrics_endpoint)
app.websocket("/ws/alerts")(websocket_alerts_endpoint)

create_clickhouse_table()


@app.get("/health")
async def health_check():
    return {"status": "ok"}


@app.on_event("startup")
async def startup_event():
    logger.info("[App] Starting Kafka consumers")
    asyncio.create_task(kafka_predictions_consumer_loop())
    asyncio.create_task(kafka_metrics_consumer_loop())
