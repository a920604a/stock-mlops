import asyncio
import json
import logging
import pandas as pd
from aiokafka import AIOKafkaConsumer
from websocket_predictions import broadcast_predictions
from websocket_metrics import broadcast_metrics
from db import insert_prediction_to_clickhouse
from evidently import Report
from evidently.metrics import (
    DatasetMissingValueCount,
    MissingValueCount,
    StdValue,
    QuantileValue,
    DuplicatedRowCount,
    MeanValue,
)


# === Logging ===
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)

# === Config ===
BASELINE_SIZE = 1  # 測試模式
DRIFT_CHECK_SIZE = 2
MAX_WINDOW_SIZE = 50

reference_data = None
current_data = pd.DataFrame()

# === Evidently Report ===
drift_report = Report(
    metrics=[
        DatasetMissingValueCount(),
        MissingValueCount(column="actual_close"),
        MeanValue(column="actual_close"),
        StdValue(column="actual_close"),
        QuantileValue(column="actual_close", quantile=0.5),
        DuplicatedRowCount(),
    ]
)

# === 工具函式 ===
def extract_metric(drift_result: dict, metric_name: str, key: str = "result") -> float:
    """從 Evidently 的結果中提取指定 metric"""
    try:
        for m in drift_result.get("metrics", []):
            if metric_name in m.get("metric_id", ""):
                return float(m[key])
    except Exception:
        return 0.0
    return 0.0


# === 主 Consumer Loop ===
async def kafka_predictions_consumer_loop():
    global current_data, reference_data

    consumer = AIOKafkaConsumer(
        "stock_predictions",
        bootstrap_servers="kafka:9092",
        group_id="prediction_dashboard",
        auto_offset_reset="latest",
    )

    while True:
        try:
            logger.info("[KafkaConsumer][predictions] Starting predictions consumer...")
            await consumer.start()
            break
        except Exception as e:
            logger.warning(
                f"[KafkaConsumer][predictions] Kafka not ready, retry in 2s: {e}"
            )
            await asyncio.sleep(2)

    try:
        async for msg in consumer:
            try:
                data = json.loads(msg.value.decode("utf-8"))
                logger.info(f"[KafkaConsumer][predictions] Received prediction: {data}")

                # Step 1: 寫入 ClickHouse
                await insert_prediction_to_clickhouse(data)

                # Step 2: 更新 Evidently data window
                current_data = pd.concat([current_data, pd.DataFrame([data])])
                if len(current_data) > MAX_WINDOW_SIZE:
                    current_data = current_data.iloc[-MAX_WINDOW_SIZE:]

                # Step 2-1: 建立 baseline
                if reference_data is None and len(current_data) >= BASELINE_SIZE:
                    reference_data = current_data.copy()
                    logger.info(
                        f"[KafkaConsumer][predictions][Evidently] Baseline established with {len(reference_data)} records"
                    )
                    # await broadcast_metrics({"type": "baseline_ready", "size": len(reference_data)})

                # Step 2-2: 執行 drift 檢查
                elif (
                    reference_data is not None and len(current_data) >= DRIFT_CHECK_SIZE
                ):
                    try:
                        snapshot = drift_report.run(
                            reference_data=reference_data, current_data=current_data
                        )
                        drift_result = snapshot.dict()

                        missing_ratio = extract_metric(
                            drift_result, "DatasetMissingValueCount", "result.share"
                        )
                        mean_val = extract_metric(
                            drift_result,
                            "MeanValue(column=actual_close)",
                            "result.value",
                        )
                        std_val = extract_metric(
                            drift_result,
                            "StdValue(column=actual_close)",
                            "result.value",
                        )

                        logger.info(
                            f"[KafkaConsumer][predictions][Evidently] Drift check results: Missing Ratio: {missing_ratio}, Mean Value: {mean_val}, Std Value: {std_val}"
                        )
                        # await broadcast_metrics({
                        #     "type": "drift_check",
                        #     "missing_ratio": missing_ratio,
                        #     "mean_value": mean_val,
                        #     "std_value": std_val,
                        # })

                    except Exception as e:
                        logger.warning(
                            f"[KafkaConsumer][predictions][Evidently] Drift check failed: {e}"
                        )

                # Step 3: 廣播 Prediction 給 WebSocket
                await broadcast_predictions(data)

            except Exception as e:
                logger.error(
                    f"[KafkaConsumer][predictions] Error processing message: {e}"
                )

    finally:
        await consumer.stop()
        logger.info("[KafkaConsumer][predictions] Predictions consumer stopped.")
