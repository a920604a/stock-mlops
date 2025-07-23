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

# === Evidently Drift Detection Config ===

# === 全域變數與設定 ===
BASELINE_SIZE = 1  # 測試模式：baseline 設定需要 5 筆
DRIFT_CHECK_SIZE = 2
DRIFT_ALERT_THRESHOLD = 0.00
MISSING_ALERT_THRESHOLD = 0.01
MAX_WINDOW_SIZE = 50


reference_data = None
current_data = pd.DataFrame()

# Evidently Report
drift_report = Report(
    metrics=[
        DatasetMissingValueCount(),
        MissingValueCount(column="Close"),
        MeanValue(column="Close"),
        StdValue(column="Close"),
        QuantileValue(column="Close", quantile=0.5),
        DuplicatedRowCount(),
    ]
)

# === 指標抽取工具函式 ===
def extract_drift_score(drift_result: dict) -> float:
    try:
        for m in drift_result.get("metrics", []):
            if "ValueDrift(column=Close)" in m.get("metric_id", ""):
                return float(m["result"]["drift_score"])
    except Exception:
        return 0.0
    return 0.0


def extract_missing_ratio(drift_result: dict) -> float:
    try:
        for m in drift_result.get("metrics", []):
            if "DatasetMissingValueCount" in m.get("metric_id", ""):
                return float(m["result"]["share"])
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

    # 連線重試
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
                if "Close" not in current_data.columns:
                    current_data["Close"] = current_data.get(
                        "actual_close", 0.0
                    )  # 使用 actual_close 取代

                if len(current_data) > MAX_WINDOW_SIZE:
                    current_data = current_data.iloc[-MAX_WINDOW_SIZE:]

                # Step 2-1: 建立 baseline
                if reference_data is None and len(current_data) >= BASELINE_SIZE:
                    reference_data = current_data.copy()
                    logger.info(
                        f"[KafkaConsumer][predictions][Evidently] Baseline established with {len(reference_data)} records"
                    )
                    await broadcast_metrics(
                        {"type": "baseline_ready", "size": len(reference_data)}
                    )

                # Step 2-2: 執行 drift 檢查
                elif (
                    reference_data is not None and len(current_data) >= DRIFT_CHECK_SIZE
                ):
                    try:
                        snapshot = drift_report.run(
                            reference_data=reference_data, current_data=current_data
                        )

                        drift_result = snapshot.dict()

                        drift_score = extract_drift_score(drift_result)
                        missing_ratio = extract_missing_ratio(drift_result)

                        # 廣播 drift metrics
                        # await broadcast_metrics({
                        #     "type": "drift_check",
                        #     "drift_score": drift_score,
                        #     "missing_ratio": missing_ratio
                        # })

                        # Step 2-3: 觸發警報
                        # if drift_score > DRIFT_ALERT_THRESHOLD or missing_ratio > MISSING_ALERT_THRESHOLD:
                        alert_msg = {
                            "type": "alert",
                            "drift_score": drift_score,
                            "missing_ratio": missing_ratio,
                            "message": "Data drift detected (testing mode)!",
                        }
                        logger.warning(f"[KafkaConsumer][Evidently][Alert] {alert_msg}")
                        # await broadcast_alert(alert_msg)

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
