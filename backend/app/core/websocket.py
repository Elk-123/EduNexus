import json
from fastapi import WebSocket


class WebSocketManager:
    """管理按 task_id 分组的 WebSocket 连接"""

    def __init__(self):
        self.connections: dict[str, list[WebSocket]] = {}

    async def connect(self, task_id: str, websocket: WebSocket):
        await websocket.accept()
        self.connections.setdefault(task_id, []).append(websocket)

    def disconnect(self, task_id: str, websocket: WebSocket):
        group = self.connections.get(task_id)
        if group:
            try:
                group.remove(websocket)
            except ValueError:
                pass
            if not group:
                del self.connections[task_id]

    async def broadcast(self, task_id: str, event: dict):
        """向监听某个 task_id 的所有连接广播事件"""
        group = self.connections.get(task_id, [])
        disconnected = []
        for ws in group:
            try:
                await ws.send_json(event)
            except Exception:
                disconnected.append(ws)
        for ws in disconnected:
            self.disconnect(task_id, ws)


ws_manager = WebSocketManager()
