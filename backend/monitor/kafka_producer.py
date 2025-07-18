from aiokafka import AIOKafkaProducer
import asyncio
import json

producer = None


async def init_kafka_producer():
    global producer
    producer = AIOKafkaProducer(bootstrap_servers="kafka:9092")
    await producer.start()


async def send_to_kafka(topic: str, message: dict):
    if producer is None:
        raise RuntimeError("Kafka producer 尚未初始化")
    await producer.send_and_wait(topic, json.dumps(message).encode("utf-8"))
