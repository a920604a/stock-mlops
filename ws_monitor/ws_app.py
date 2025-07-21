from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from aiokafka import AIOKafkaConsumer
import asyncio
import json
from db import insert_prediction_to_clickhouse
import logging

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

app = FastAPI()
connections = set()


@app.websocket("/ws/predictions")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    connections.add(websocket)
    logger.info(f"[WebSocket] Client connected: {websocket.client}")
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        connections.remove(websocket)
        logger.info(f"[WebSocket] Client disconnected: {websocket.client}")


async def broadcast(message: dict):
    to_remove = []
    logger.info(f"[Broadcast] Sending message to {len(connections)} clients: {message}")
    for conn in connections:
        try:
            await conn.send_text(json.dumps(message))
        except Exception as e:
            logger.info(f"[Broadcast] Error sending to client {conn.client}: {e}")
            to_remove.append(conn)
    for conn in to_remove:
        connections.remove(conn)


async def kafka_consumer_loop():
    consumer = AIOKafkaConsumer(
        "stock_predictions",
        bootstrap_servers="kafka:9092",
        group_id="prediction_dashboard",
        auto_offset_reset="latest",
    )
    logger.info("[KafkaConsumer] Starting consumer...")
    await consumer.start()
    try:
        async for msg in consumer:
            data = json.loads(msg.value.decode("utf-8"))
            logger.info(f"[KafkaConsumer] Received message: {data}")

            # **1. 寫入 ClickHouse**
            logger.info("[ClickHouse] Inserting prediction data...")
            await insert_prediction_to_clickhouse(data)
            logger.info("[ClickHouse] Insert success.")

            # **2. 廣播到 WebSocket**
            logger.info("[WebSocket] Broadcasting prediction data...")
            await broadcast(data)

    finally:
        await consumer.stop()
        logger.info("[KafkaConsumer] Consumer stopped.")


@app.on_event("startup")
async def startup_event():
    logger.info("[App] Startup event: launching kafka_consumer_loop task")
    asyncio.create_task(kafka_consumer_loop())
