import json
import asyncio
from aiokafka import AIOKafkaProducer
from aiokafka.errors import KafkaConnectionError

# 預測 API + Kafka Producer
producer = None


async def init_kafka_producer():
    global producer
    retries = 5
    for i in range(retries):
        try:
            producer = AIOKafkaProducer(bootstrap_servers="kafka:9092")
            await producer.start()
            print("Kafka Producer 已啟動")
            return
        except KafkaConnectionError:
            print(f"無法連接 Kafka, {i+1}/{retries} 重試中...")
            await asyncio.sleep(5)
    raise RuntimeError("無法連接 Kafka, 已達重試上限")


async def send_prediction_to_kafka(prediction: dict):
    if producer is None:
        await init_kafka_producer()
    print("send_prediction_to_kafka")
    await producer.send_and_wait(
        "stock_predictions", json.dumps(prediction).encode("utf-8")
    )


async def close_kafka_producer():
    global producer
    if producer:
        await producer.stop()
        print("🛑 Kafka Producer 已關閉")
