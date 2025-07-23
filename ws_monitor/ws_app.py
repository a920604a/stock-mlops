from fastapi import FastAPI
import logging
import asyncio

from websocket_predictions import websocket_predictions_endpoint
from websocket_metrics import websocket_metrics_endpoint
from kafka_predictions_consumer import kafka_predictions_consumer_loop
from kafka_metrics_consumer import kafka_metrics_consumer_loop

app = FastAPI()
logger = logging.getLogger(__name__)

# WebSocket 路由註冊
app.websocket("/ws/predictions")(websocket_predictions_endpoint)
app.websocket("/ws/metrics")(websocket_metrics_endpoint)


@app.on_event("startup")
async def startup_event():
    logger.info("[App] Starting Kafka consumers")
    asyncio.create_task(kafka_predictions_consumer_loop())
    asyncio.create_task(kafka_metrics_consumer_loop())
