"""
WebSocket 协商聊天处理
"""
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Dict, Set
import json
import logging
from datetime import datetime

from app.core.database import AsyncSessionLocal
from app.core.security import decode_token
from app.models.models import User, NegotiationMessage, MessageType, UserStatus

router = APIRouter()
logger = logging.getLogger(__name__)

# 连接管理器
class ConnectionManager:
    def __init__(self):
        # case_id -> Set[WebSocket]
        self.active_connections: Dict[int, Set[WebSocket]] = {}
        # websocket -> user_id
        self.user_map: Dict[WebSocket, int] = {}

    async def connect(self, websocket: WebSocket, case_id: int, user_id: int):
        await websocket.accept()
        if case_id not in self.active_connections:
            self.active_connections[case_id] = set()
        self.active_connections[case_id].add(websocket)
        self.user_map[websocket] = user_id
        logger.info(f"WS 用户 {user_id} 加入案件 {case_id}")

    def disconnect(self, websocket: WebSocket, case_id: int):
        if case_id in self.active_connections:
            self.active_connections[case_id].discard(websocket)
        self.user_map.pop(websocket, None)

    async def broadcast_to_case(self, case_id: int, message: dict, exclude_ws: WebSocket = None):
        """向案件所有连接广播消息"""
        connections = self.active_connections.get(case_id, set()).copy()
        dead = set()
        for ws in connections:
            if ws == exclude_ws:
                continue
            try:
                await ws.send_json(message)
            except Exception:
                dead.add(ws)
        for ws in dead:
            self.active_connections[case_id].discard(ws)


manager = ConnectionManager()


@router.websocket("/chat/{case_id}")
async def websocket_chat(
    websocket: WebSocket,
    case_id: int,
    token: str = Query(...),
):
    """WebSocket 实时聊天"""
    # 验证 JWT
    payload = decode_token(token)
    if not payload:
        await websocket.close(code=4001)
        return

    user_id = int(payload.get("sub", 0))

    async with AsyncSessionLocal() as db:
        result = await db.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()
        if not user or user.status != UserStatus.ACTIVE:
            await websocket.close(code=4003)
            return

    await manager.connect(websocket, case_id, user_id)

    try:
        while True:
            raw = await websocket.receive_text()
            data = json.loads(raw)
            msg_type = data.get("type", "text")
            content = data.get("content", "")

            # 保存消息到数据库
            async with AsyncSessionLocal() as db:
                msg = NegotiationMessage(
                    case_id=case_id,
                    sender_id=user_id,
                    message_type=MessageType(msg_type) if msg_type in MessageType.__members__.values() else MessageType.TEXT,
                    content=content,
                )
                db.add(msg)
                await db.commit()
                await db.refresh(msg)

                # 获取发送者信息
                user_result = await db.execute(select(User).where(User.id == user_id))
                sender = user_result.scalar_one_or_none()

            broadcast_msg = {
                "id": msg.id,
                "case_id": case_id,
                "sender_id": user_id,
                "sender_name": sender.real_name if sender else "未知",
                "message_type": msg_type,
                "content": content,
                "created_at": msg.created_at.isoformat(),
            }

            # 广播给同一案件所有连接（包括自己）
            await manager.broadcast_to_case(case_id, broadcast_msg)

    except WebSocketDisconnect:
        manager.disconnect(websocket, case_id)
        logger.info(f"WS 用户 {user_id} 离开案件 {case_id}")
    except Exception as e:
        logger.error(f"WS 异常: {e}")
        manager.disconnect(websocket, case_id)
