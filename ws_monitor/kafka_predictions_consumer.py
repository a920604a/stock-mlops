import asyncio
import json
import logging
import pandas as pd
from dataclasses import dataclass, field
from aiokafka import AIOKafkaConsumer

from websocket_predictions import broadcast_predictions
from websocket_anomalies import broadcast_alert
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

# === Evidently 報告 ===
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


@dataclass
class EvidentlyState:
    reference_data: pd.DataFrame = None
    current_data: pd.DataFrame = field(default_factory=pd.DataFrame)
    baseline_metrics: dict = field(default_factory=dict)


state = EvidentlyState()

# === 工具函式 ===
def extract_metric_value(drift_result: dict, metric_name: str, column: str = None):
    """從 Evidently 結果提取特定 metric 值"""
    for m in drift_result.get("metrics", []):
        mid = m.get("metric_id", "")
        val = m.get("value", m.get("result"))

        if metric_name == "DatasetMissingValueCount" and metric_name in mid:
            return float(val.get("share", 0.0)) if isinstance(val, dict) else float(val)
        if metric_name == "MissingValueCount" and f"({column})" in mid:
            return float(val.get("count", 0)) if isinstance(val, dict) else float(val)
        if metric_name in mid and column and f"({column})" in mid:
            return float(val) if val is not None else 0.0
        if metric_name == "DuplicatedRowCount" and metric_name in mid:
            return int(val.get("count", 0)) if isinstance(val, dict) else int(val or 0)
    return 0.0


def calculate_baseline_metrics(reference_data: pd.DataFrame) -> dict:
    snapshot = drift_report.run(
        reference_data=reference_data, current_data=reference_data
    )
    result = snapshot.dict()
    metrics_dict = {}
    for metric in result.get("metrics", []):
        if "MeanValue" in metric.get("metric_id", ""):
            metrics_dict["MeanValue_actual_close"] = metric.get("result", 0.0)
        elif "StdValue" in metric.get("metric_id", ""):
            metrics_dict["StdValue_actual_close"] = metric.get("result", 0.0)
    return metrics_dict


def check_anomalies(drift_result: dict, baseline_metrics: dict):
    """根據 drift_result 和 baseline_metrics 判斷是否異常"""
    alerts = []
    MISSING_RATIO_THRESHOLD = 0.05
    MISSING_COUNT_THRESHOLD = 5
    MEAN_DIFF_THRESHOLD = 10.0
    STD_DIFF_THRESHOLD = 5.0
    DUPLICATED_COUNT_THRESHOLD = 10

    current_missing_ratio = extract_metric_value(
        drift_result, "DatasetMissingValueCount"
    )
    if current_missing_ratio > MISSING_RATIO_THRESHOLD:
        alerts.append(f"Missing ratio too high: {current_missing_ratio:.2f}")

    current_missing_count = extract_metric_value(
        drift_result, "MissingValueCount", "actual_close"
    )
    if current_missing_count > MISSING_COUNT_THRESHOLD:
        alerts.append(
            f"Missing count for actual_close too high: {current_missing_count}"
        )

    current_mean = extract_metric_value(drift_result, "MeanValue", "actual_close")
    baseline_mean = baseline_metrics.get("MeanValue_actual_close")
    if (
        baseline_mean is not None
        and abs(current_mean - baseline_mean) > MEAN_DIFF_THRESHOLD
    ):
        alerts.append(
            f"Mean drift detected: baseline={baseline_mean:.2f}, current={current_mean:.2f}"
        )

    current_std = extract_metric_value(drift_result, "StdValue", "actual_close")
    baseline_std = baseline_metrics.get("StdValue_actual_close")
    if (
        baseline_std is not None
        and abs(current_std - baseline_std) > STD_DIFF_THRESHOLD
    ):
        alerts.append(
            f"Std drift detected: baseline={baseline_std:.2f}, current={current_std:.2f}"
        )

    duplicated_count = extract_metric_value(drift_result, "DuplicatedRowCount")
    if duplicated_count > DUPLICATED_COUNT_THRESHOLD:
        alerts.append(f"Duplicated rows count too high: {duplicated_count}")

    return (
        {"type": "alert", "messages": alerts, "drift_result": drift_result}
        if alerts
        else None
    )


async def check_with_evidently(data: dict, state: EvidentlyState):
    """更新資料並使用 Evidently 驗證"""
    state.current_data = pd.concat([state.current_data, pd.DataFrame([data])])
    if len(state.current_data) > MAX_WINDOW_SIZE:
        state.current_data = state.current_data.iloc[-MAX_WINDOW_SIZE:]

    # 設定 baseline
    if state.reference_data is None and len(state.current_data) >= BASELINE_SIZE:
        state.reference_data = state.current_data.copy()
        state.baseline_metrics = calculate_baseline_metrics(state.reference_data)
        logger.info(
            f"[Evidently] Baseline established with {len(state.reference_data)} records"
        )
        logger.info(f"[Evidently] Baseline metrics: {state.baseline_metrics}")
        return None

    # Drift 檢查
    if state.reference_data is not None and len(state.current_data) >= DRIFT_CHECK_SIZE:
        try:
            snapshot = drift_report.run(
                reference_data=state.reference_data,
                current_data=state.current_data,
            )
            drift_result = snapshot.dict()
            alert_msg = check_anomalies(drift_result, state.baseline_metrics)
            return alert_msg
        except Exception as e:
            logger.warning(f"[Evidently] Drift check failed: {e}")
    return None


# === 消費者邏輯 ===
async def process_prediction(data: dict, state: EvidentlyState):
    """處理單筆 Kafka 預測訊息"""
    try:
        await insert_prediction_to_clickhouse(data)
        alert_msg = await check_with_evidently(data, state)
        if alert_msg:
            await broadcast_alert(alert_msg)
        await broadcast_predictions(data)
    except Exception as e:
        logger.error(f"[KafkaConsumer][predictions] Error processing prediction: {e}")


async def start_kafka_consumer_with_retry(consumer: AIOKafkaConsumer):
    while True:
        try:
            await consumer.start()
            logger.info("[KafkaConsumer][predictions] Consumer started.")
            break
        except Exception as e:
            logger.warning(
                f"[KafkaConsumer][predictions] Kafka not ready, retry in 2s: {e}"
            )
            await asyncio.sleep(2)


# === 主 Consumer Loop ===
async def kafka_predictions_consumer_loop():
    consumer = AIOKafkaConsumer(
        "stock_predictions",
        bootstrap_servers="kafka:9092",
        group_id="prediction_dashboard",
        auto_offset_reset="latest",
    )

    await start_kafka_consumer_with_retry(consumer)

    try:
        async for msg in consumer:
            data = json.loads(msg.value.decode("utf-8"))
            logger.info(f"[KafkaConsumer][predictions] Received prediction: {data}")
            await process_prediction(data, state)
    finally:
        await consumer.stop()
        logger.info("[KafkaConsumer][predictions] Consumer stopped.")
