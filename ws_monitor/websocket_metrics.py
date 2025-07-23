from fastapi import WebSocket, WebSocketDisconnect
import json
import logging

logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

metrics_connections = set()


async def websocket_metrics_endpoint(websocket: WebSocket):
    await websocket.accept()
    metrics_connections.add(websocket)
    logger.info(f"[WebSocket][metrics] Client connected: {websocket.client}")
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        metrics_connections.remove(websocket)
        logger.info(f"[WebSocket][metrics] Client disconnected: {websocket.client}")


async def broadcast_metrics(message: dict):
    to_remove = []
    # logger.info(
    #     f"[Broadcast][metrics] Sending to {len(metrics_connections)} clients: {message}"
    # )
    for conn in metrics_connections:
        try:
            await conn.send_text(json.dumps(message))
        except Exception as e:
            logger.warning(f"[Broadcast][metrics] Error sending to {conn.client}: {e}")
            to_remove.append(conn)
    for conn in to_remove:
        metrics_connections.remove(conn)
