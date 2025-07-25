import asyncio
import json
import logging

import pandas as pd
from aiokafka import AIOKafkaConsumer
from websocket_metrics import broadcast_metrics

# === Logging ===
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)


reference_data = None
current_data = pd.DataFrame()


async def kafka_metrics_consumer_loop():
    """
    Consumer for system monitoring metrics (Prometheus compatible).
    """
    consumer = AIOKafkaConsumer(
        "monitoring_metrics",
        bootstrap_servers="kafka:9092",
        group_id="metrics_dashboard",
        auto_offset_reset="latest",
    )

    while True:
        try:
            logger.info("[KafkaConsumer][metrics] Starting metrics consumer...")
            await consumer.start()
            break
        except Exception as e:
            logger.warning(
                f"[KafkaConsumer][metrics] Kafka not ready, retry in 2s: {e}"
            )
            await asyncio.sleep(2)

    try:
        async for msg in consumer:
            try:
                data = json.loads(msg.value.decode("utf-8"))
                # logger.info(f"[KafkaConsumer][metrics] Received metric: {data}")
                await broadcast_metrics(data)
            except Exception as e:
                logger.error(f"[KafkaConsumer][metrics] Error processing message: {e}")

    finally:
        await consumer.stop()
        logger.info("[KafkaConsumer] Metrics consumer stopped.")
