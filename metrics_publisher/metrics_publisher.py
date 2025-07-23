import asyncio
import aiohttp
import json
import time
import logging
from aiokafka import AIOKafkaProducer

PROMETHEUS_ENDPOINT = "http://backend1:8000/metrics"  # backend 暴露的 /metrics
KAFKA_BOOTSTRAP_SERVERS = "kafka:9092"
TOPIC = "monitoring_metrics"

# 設定 logger
logger = logging.getLogger("metrics_publisher")
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)


async def init_kafka_producer():
    producer = AIOKafkaProducer(bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS)
    while True:
        try:
            await producer.start()
            logger.info("Kafka Producer 已啟動")
            return producer
        except Exception as e:
            logger.warning(f"Kafka Producer 啟動失敗，2 秒後重試... ({e})")
            await asyncio.sleep(2)


async def fetch_prometheus_metrics():
    """
    從 Prometheus endpoint 抓取 metrics
    """
    async with aiohttp.ClientSession() as session:
        async with session.get(PROMETHEUS_ENDPOINT) as resp:
            if resp.status != 200:
                raise RuntimeError(f"Prometheus endpoint error: {resp.status}")
            return await resp.text()


def parse_prometheus_metrics(raw_metrics: str):
    """
    解析 Prometheus metrics，僅取出我們關心的指標：
    cpu_usage_seconds_total, memory_resident_bytes,
    http_requests_total, http_request_duration_avg,
    predict_success_total, predict_failure_total,
    predict_duration_avg, active_websocket_clients
    """
    metrics = {}
    histogram_sums = {}
    histogram_counts = {}

    for line in raw_metrics.split("\n"):
        if line.startswith("#") or not line.strip():
            continue

        parts = line.split(" ")
        key = parts[0]
        try:
            value = float(parts[-1]) if parts[-1] else 0
        except Exception as e:
            logger.warning(f"解析數值失敗 ({key}): {e}")
            continue

        # 基本指標
        if key == "process_cpu_seconds_total":
            metrics["cpu_usage_seconds_total"] = value
        elif key == "process_resident_memory_bytes":
            metrics["memory_resident_bytes"] = value
        elif key.startswith("http_requests_total"):
            # 可能有 label，要直接覆蓋或累加
            # 這裡先簡單累加（或只取第一筆）
            if "http_requests_total" not in metrics:
                metrics["http_requests_total"] = 0
            metrics["http_requests_total"] += value
        elif key == "predict_success_total":
            metrics["predict_success_total"] = value
        elif key == "predict_failure_total":
            metrics["predict_failure_total"] = value
        elif key == "active_websocket_clients":
            metrics["active_websocket_clients"] = value

        # Histogram sum/count 用來計算平均延遲
        elif key == "http_request_duration_seconds_sum":
            histogram_sums["http_request_duration"] = value
        elif key == "http_request_duration_seconds_count":
            histogram_counts["http_request_duration"] = value
        elif key == "predict_duration_seconds_sum":
            histogram_sums["predict_duration"] = value
        elif key == "predict_duration_seconds_count":
            histogram_counts["predict_duration"] = value

    # 計算平均延遲 (秒)
    if histogram_counts.get("http_request_duration", 0) > 0:
        metrics["http_request_duration_avg"] = (
            histogram_sums["http_request_duration"]
            / histogram_counts["http_request_duration"]
        )
    else:
        metrics["http_request_duration_avg"] = 0

    if histogram_counts.get("predict_duration", 0) > 0:
        metrics["predict_duration_avg"] = (
            histogram_sums["predict_duration"] / histogram_counts["predict_duration"]
        )
    else:
        metrics["predict_duration_avg"] = 0

    return metrics


async def publish_metrics(interval: int = 5):
    producer = await init_kafka_producer()
    try:
        while True:
            try:
                raw_metrics = await fetch_prometheus_metrics()
                metrics = parse_prometheus_metrics(raw_metrics)
                payload = {"timestamp": int(time.time()), "metrics": metrics}
                await producer.send_and_wait(TOPIC, json.dumps(payload).encode("utf-8"))
                logger.info(f"已發送指標: {payload}")
            except Exception as e:
                logger.error(f"抓取或發送指標失敗: {e}")
            await asyncio.sleep(interval)
    finally:
        await producer.stop()
        logger.info("Kafka Producer 已關閉")


if __name__ == "__main__":
    asyncio.run(publish_metrics())
