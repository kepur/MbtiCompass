from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Depends
from typing import Dict
import json

app = FastAPI()

# 维护用户的 WebSocket 连接
active_connections: Dict[int, WebSocket] = {}

@app.websocket("/ws/{user_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: int):
    """ WebRTC 信令服务器 """
    await websocket.accept()
    active_connections[user_id] = websocket

    try:
        while True:
            data = await websocket.receive_text()
            message = json.loads(data)

            action = message.get("action")
            target_user = message.get("target_user")

            if action == "offer":
                if target_user in active_connections:
                    await active_connections[target_user].send_text(json.dumps({
                        "action": "offer",
                        "sdp": message["sdp"],
                        "from": user_id
                    }))

            elif action == "answer":
                if target_user in active_connections:
                    await active_connections[target_user].send_text(json.dumps({
                        "action": "answer",
                        "sdp": message["sdp"],
                        "from": user_id
                    }))

            elif action == "ice-candidate":
                if target_user in active_connections:
                    await active_connections[target_user].send_text(json.dumps({
                        "action": "ice-candidate",
                        "candidate": message["candidate"],
                        "from": user_id
                    }))

    except WebSocketDisconnect:
        del active_connections[user_id]
