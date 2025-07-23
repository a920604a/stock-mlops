import asyncio
import json
from aiokafka import AIOKafkaConsumer
import logging
from websocket_predictions import broadcast_predictions
from websocket_metrics import broadcast_metrics
from db import insert_prediction_to_clickhouse

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)


async def kafka_predictions_consumer_loop():
    consumer = AIOKafkaConsumer(
        "stock_predictions",
        bootstrap_servers="kafka:9092",
        group_id="prediction_dashboard",
        auto_offset_reset="latest",
    )

    while True:
        try:
            logger.info("[KafkaConsumer] Starting predictions consumer...")
            await consumer.start()
            break
        except Exception as e:
            logger.warning(f"[KafkaConsumer] Kafka not ready, retry in 2s: {e}")
            await asyncio.sleep(2)

    try:
        async for msg in consumer:
            data = json.loads(msg.value.decode("utf-8"))
            logger.info(f"[KafkaConsumer] Received prediction: {data}")

            # 寫入 ClickHouse
            logger.info("[ClickHouse] Inserting prediction data...")
            await insert_prediction_to_clickhouse(data)
            logger.info("[ClickHouse] Insert success.")

            # 廣播
            await broadcast_predictions(data)
    finally:
        await consumer.stop()
        logger.info("[KafkaConsumer] Predictions consumer stopped.")


async def kafka_metrics_consumer_loop():
    consumer = AIOKafkaConsumer(
        "monitoring_metrics",
        bootstrap_servers="kafka:9092",
        group_id="metrics_dashboard",
        auto_offset_reset="latest",
    )
    await consumer.start()
    try:
        async for msg in consumer:
            data = json.loads(msg.value.decode("utf-8"))
            logger.info(f"[KafkaConsumer][metrics] Received metric: {data}")
            await broadcast_metrics(data)
    finally:
        await consumer.stop()
        logger.info("[KafkaConsumer] Metrics consumer stopped.")
