from fastapi import WebSocket, WebSocketDisconnect
import json
import logging

logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

# 假設你有一個全域的連線集合
connected_websockets = set()


async def websocket_alerts_endpoint(websocket: WebSocket):
    await websocket.accept()
    connected_websockets.add(websocket)
    logger.info(f"[WebSocket][alerts] Client connected: {websocket.client}")
    try:
        while True:
            # 持續等待訊息（前端可發心跳或其他訊息）
            await websocket.receive_text()

    except WebSocketDisconnect:
        connected_websockets.remove(websocket)
        logger.info(f"[WebSocket][alerts] Client disconnected: {websocket.client}")


async def broadcast_alert(alert_msg: dict):
    # if not connected_websockets:
    #     return
    logger.info(
        f"[Broadcast][alerts] Sending to {len(connected_websockets)} clients: {alert_msg}"
    )

    to_remove = []
    for ws in connected_websockets:
        try:
            await ws.send_text(json.dumps(alert_msg))
        except Exception as e:
            # 你也可以紀錄或處理其他異常
            logger.warning(f"[Broadcast][alerts] Error sending to {ws.client}: {e}")

            to_remove.append(ws)

    # 清除已斷線的連線
    for ws in to_remove:
        connected_websockets.remove(ws)
