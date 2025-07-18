# api/routes/ws_monitor.py
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
import json
from aiokafka import AIOKafkaConsumer
import asyncio

router = APIRouter()


class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            try:
                await connection.send_text(message)
            except Exception:
                pass


manager = ConnectionManager()


@router.websocket("/ws/stock_monitoring")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            _ = await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)


# Kafka 消費者背景任務
async def kafka_consumer_loop():
    consumer = AIOKafkaConsumer(
        "stock_monitoring_topic",
        bootstrap_servers="kafka:9092",
        group_id="stock_monitoring_group",
        max_poll_interval_ms=600000,  # 延長到 10 分鐘
        max_poll_records=10,  # 每次最多拉 10 筆消息
    )

    await consumer.start()
    try:
        async for msg in consumer:
            event = json.loads(msg.value.decode("utf-8"))
            await manager.broadcast(json.dumps(event))
    finally:
        await consumer.stop()


def start_kafka_consumer():
    asyncio.create_task(kafka_consumer_loop())
