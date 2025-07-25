import datetime
import json
import logging

import pandas as pd
from evidently import Report
from evidently.metrics import MAE, RMSE, DatasetMissingValueCount, ValueDrift
from fastapi import WebSocket, WebSocketDisconnect

logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

connections = set()

# === Evidently baseline & sliding window ===
BASELINE_SIZE = 50
MAX_WINDOW_SIZE = 100
reference_dataset = None
current_data = pd.DataFrame()

# === 建立 Evidently 報告 ===
def create_evidently_report():
    return Report(
        metrics=[DatasetMissingValueCount(), ValueDrift(column="Close"), MAE(), RMSE()]
    )


def extract_metric_value(metrics, metric_key_prefix: str):
    for m in metrics:
        if metric_key_prefix in m.get("metric_id", ""):
            return m.get("value", 0.0)
    return 0.0


async def websocket_predictions_endpoint(websocket: WebSocket):
    await websocket.accept()
    connections.add(websocket)
    logger.info(f"[WebSocket][predictions] Client connected: {websocket.client}")
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        connections.remove(websocket)
        logger.info(f"[WebSocket][predictions] Client disconnected: {websocket.client}")


async def broadcast_predictions(message: dict):
    to_remove = []
    logger.info(
        f"[Broadcast][predictions] Sending to {len(connections)} clients: {message}"
    )
    for conn in connections:
        try:
            await conn.send_text(json.dumps(message))
        except Exception as e:
            logger.warning(
                f"[Broadcast][predictions] Error sending to {conn.client}: {e}"
            )
            to_remove.append(conn)
    for conn in to_remove:
        connections.remove(conn)


def get_monitoring_metrics() -> dict:
    global reference_dataset, current_data

    if reference_dataset is None or len(current_data) < 10:
        return {"status": "insufficient_data", "size": len(current_data)}

    report = create_evidently_report()
    snapshot = report.run(
        reference_data=reference_dataset,
        current_data=current_data,
    )
    metrics = snapshot.dict()["metrics"]

    prediction_drift = extract_metric_value(metrics, "ValueDrift(column=Close)")
    drift_alert = prediction_drift > 0.2

    return {
        "timestamp": datetime.datetime.now().isoformat(),
        "prediction_drift": prediction_drift,
        "mae": extract_metric_value(metrics, "MAE"),
        "rmse": extract_metric_value(metrics, "RMSE"),
        "alert": drift_alert,
    }


def update_data_stream(new_data: dict):
    """
    新增新資料到 current_data，並自動建立 baseline
    """
    global reference_dataset, current_data

    df_new = pd.DataFrame([new_data])
    current_data = pd.concat([current_data, df_new])
    if len(current_data) > MAX_WINDOW_SIZE:
        current_data = current_data.iloc[-MAX_WINDOW_SIZE:]

    if reference_dataset is None and len(current_data) >= BASELINE_SIZE:
        reference_dataset = current_data.copy()
        logger.info(f"[Evidently] Baseline created with {len(reference_dataset)} rows.")
