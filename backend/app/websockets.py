import asyncio
import json
import os
from typing import Dict, Any
from fastapi import WebSocket, WebSocketDisconnect

try:
    import redis
except Exception:
    redis = None

REDIS_URL = os.environ.get("REDIS_URL", "redis://redis:6379/0")


class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}

    async def connect(self, websocket: WebSocket, client_id: str):
        await websocket.accept()
        self.active_connections[client_id] = websocket

    def disconnect(self, client_id: str):
        if client_id in self.active_connections:
            del self.active_connections[client_id]

    async def send_personal_message(self, client_id: str, message: Dict[str, Any]):
        ws = self.active_connections.get(client_id)
        if ws:
            await ws.send_text(json.dumps(message, default=str))


manager = ConnectionManager()


async def redis_subscriber(loop=None):
    if redis is None:
        return
    r = redis.from_url(REDIS_URL)
    pubsub = r.pubsub()
    pubsub.subscribe("broadcast")
    try:
        while True:
            message = pubsub.get_message(ignore_subscribe_messages=True, timeout=1.0)
            if message:
                data = message.get('data')
                if isinstance(data, bytes):
                    try:
                        payload = json.loads(data.decode('utf-8'))
                    except Exception:
                        payload = None
                    if payload and 'target_user' in payload:
                        # route to personal connection if connected
                        target = payload.get('target_user')
                        if target in manager.active_connections:
                            await manager.send_personal_message(target, payload)
            await asyncio.sleep(0)
    finally:
        try:
            pubsub.close()
        except Exception:
            pass


async def websocket_endpoint(websocket: WebSocket):
    # Expect client to send a JSON connect message containing client_id/user_id
    await websocket.accept()
    try:
        raw = await websocket.receive_text()
        msg = json.loads(raw)
        client_id = msg.get('client_id') or msg.get('user_id')
        if not client_id:
            await websocket.close(code=4001)
            return
        await manager.connect(websocket, client_id)
        while True:
            data = await websocket.receive_text()
            # for now just echo or ignore
            try:
                payload = json.loads(data)
            except Exception:
                payload = {"raw": data}
            # No-op: real routing will be implemented later
    except WebSocketDisconnect:
        if 'client_id' in locals() and client_id:
            manager.disconnect(client_id)
    except Exception:
        if 'client_id' in locals() and client_id:
            manager.disconnect(client_id)
        try:
            await websocket.close()
        except Exception:
            pass
