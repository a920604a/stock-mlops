from fastapi import WebSocket, WebSocketDisconnect
import json
import logging

logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

connections = set()


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
