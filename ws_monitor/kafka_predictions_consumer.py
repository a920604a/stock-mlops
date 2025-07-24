import asyncio
import json
import logging
import pandas as pd
from aiokafka import AIOKafkaConsumer
from websocket_predictions import broadcast_predictions
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
from websocket_anomalies import broadcast_alert

from websocket_metrics import broadcast_metrics

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
        MissingValueCount(column="actual_close"),
        MeanValue(column="actual_close"),
        StdValue(column="actual_close"),
        QuantileValue(column="actual_close", quantile=0.5),
        DuplicatedRowCount(),
    ]
)

# === 指標抽取工具函式 ===
def extract_metric_value(drift_result: dict, metric_name: str, column: str = None):
    for m in drift_result.get("metrics", []):
        mid = m.get("metric_id", "")
        if metric_name == "DatasetMissingValueCount" and metric_name in mid:
            val = m.get("value", {})
            if isinstance(val, dict):
                return float(val.get("share", 0.0))
            else:
                return float(val)
        elif metric_name == "MissingValueCount" and f"({column})" in mid:
            val = m.get("value", {})
            if isinstance(val, dict):
                return float(val.get("count", 0))
            else:
                return float(val)
        elif metric_name == "MeanValue" and f"({column})" in mid:
            val = m.get("value")
            if val is None:
                val = m.get("result")
            return float(val) if val is not None else 0.0
        elif metric_name == "StdValue" and f"({column})" in mid:
            val = m.get("value")
            if val is None:
                val = m.get("result")
            return float(val) if val is not None else 0.0
        elif metric_name == "QuantileValue" and f"({column})" in mid:
            val = m.get("value")
            if val is None:
                val = m.get("result")
            return float(val) if val is not None else 0.0
        elif metric_name == "DuplicatedRowCount" and metric_name in mid:
            val = m.get("value")
            if isinstance(val, dict):
                return int(val.get("count", 0))
            return int(val) if val is not None else 0
    return 0.0


def calculate_baseline_metrics(reference_data):
    snapshot = drift_report.run(
        reference_data=reference_data, current_data=reference_data
    )
    result = snapshot.dict()
    metrics_dict = {}
    for metric in result.get("metrics", []):
        metric_id = metric.get("metric_id")
        if "MeanValue" in metric_id:
            metrics_dict["MeanValue_actual_close"] = metric.get("result", 0.0)
        elif "StdValue" in metric_id:
            metrics_dict["StdValue_actual_close"] = metric.get("result", 0.0)
        # 可擴充更多指標
    return metrics_dict


def check_anomalies(drift_result):
    alerts = []

    # 閾值設定（可根據需求調整）
    MISSING_RATIO_THRESHOLD = 0.05
    MISSING_COUNT_THRESHOLD = 5
    MEAN_DIFF_THRESHOLD = 10.0
    STD_DIFF_THRESHOLD = 5.0
    DUPLICATED_COUNT_THRESHOLD = 10

    current_missing_ratio = extract_metric_value(
        drift_result, "DatasetMissingValueCount"
    )
    if current_missing_ratio and current_missing_ratio > MISSING_RATIO_THRESHOLD:
        alerts.append(f"Missing ratio too high: {current_missing_ratio:.2f}")

    current_missing_count = extract_metric_value(
        drift_result, "MissingValueCount", "actual_close"
    )
    if current_missing_count and current_missing_count > MISSING_COUNT_THRESHOLD:
        alerts.append(
            f"Missing count for actual_close too high: {current_missing_count}"
        )

    current_mean = extract_metric_value(drift_result, "MeanValue", "actual_close")
    baseline_mean = baseline_metrics_dict.get("MeanValue_actual_close", None)
    if (
        current_mean is not None
        and baseline_mean is not None
        and abs(current_mean - baseline_mean) > MEAN_DIFF_THRESHOLD
    ):
        alerts.append(
            f"Mean value drift detected: baseline={baseline_mean:.2f}, current={current_mean:.2f}"
        )

    current_std = extract_metric_value(drift_result, "StdValue", "actual_close")
    baseline_std = baseline_metrics_dict.get("StdValue_actual_close", None)
    if (
        current_std is not None
        and baseline_std is not None
        and abs(current_std - baseline_std) > STD_DIFF_THRESHOLD
    ):
        alerts.append(
            f"Std deviation drift detected: baseline={baseline_std:.2f}, current={current_std:.2f}"
        )

    duplicated_count = extract_metric_value(drift_result, "DuplicatedRowCount")
    if duplicated_count and duplicated_count > DUPLICATED_COUNT_THRESHOLD:
        alerts.append(f"Duplicated rows count too high: {duplicated_count}")

    if alerts:
        return {"type": "alert", "messages": alerts, "drift_result": drift_result}
    return None


# === 主 Consumer Loop ===
async def kafka_predictions_consumer_loop():
    global current_data, reference_data, baseline_metrics_dict

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
                if "Close" not in current_data.columns:
                    current_data["Close"] = current_data.get("actual_close", 0.0)

                if len(current_data) > MAX_WINDOW_SIZE:
                    current_data = current_data.iloc[-MAX_WINDOW_SIZE:]

                # Step 2-1: 建立 baseline 並計算 baseline 指標
                if reference_data is None and len(current_data) >= BASELINE_SIZE:
                    reference_data = current_data.copy()
                    baseline_metrics_dict = calculate_baseline_metrics(reference_data)
                    logger.info(
                        f"[KafkaConsumer][predictions][Evidently] Baseline established with {len(reference_data)} records"
                    )
                    logger.info(
                        f"[KafkaConsumer][Evidently] Baseline metrics: {baseline_metrics_dict}"
                    )

                # Step 2-2: 執行 drift 檢查及異常判斷
                elif (
                    reference_data is not None and len(current_data) >= DRIFT_CHECK_SIZE
                ):
                    try:
                        snapshot = drift_report.run(
                            reference_data=reference_data, current_data=current_data
                        )
                        drift_result = snapshot.dict()
                        logger.info(
                            f"[KafkaConsumer][predictions][Evidently] Drift check result: {drift_result}"
                        )

                        # 呼叫異常判斷
                        alert_msg = check_anomalies(drift_result)

                        if alert_msg:
                            logger.warning(
                                f"[KafkaConsumer][Evidently][Alert] {alert_msg}"
                            )
                            # 如有 WebSocket alert 功能，這裡可開啟
                            await broadcast_alert(alert_msg)
                            # await broadcast_metrics(alert_msg)

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
