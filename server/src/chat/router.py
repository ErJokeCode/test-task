import asyncio
from datetime import datetime, timezone
import logging

from aiogram import Bot
from fastapi import APIRouter, Request, WebSocket, WebSocketDisconnect
from fastapi.exceptions import HTTPException
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from config import settings
from models.chat.tg_user import TgUser
from models.chat.message import Message, MessageAdmin, MessageUser
from database.database import m_databese
from models.base import Resp, Sender
from chat.manager_ws import ws_chat_manager


_log = logging.getLogger(__name__)


templates = Jinja2Templates(directory="templates")

router = APIRouter(
    prefix="/chat",
    tags=["Chat"],
)


@router.get("/", response_class=HTMLResponse)
async def get_chats(request: Request):
    users = m_databese.tg_user.find()
    _log.info(users)
    return templates.TemplateResponse(
        request=request, name="item.html", context={"users": users}
    )


@router.post("/bot/user")
async def add_user_tg(
    user: TgUser
) -> Resp:
    if m_databese.tg_user.find_one(user_id=user.user_id) is not None:
        raise HTTPException(status_code=400, detail="User already exists")
    m_databese.tg_user.insert_one(user)
    await ws_chat_manager.new_user(user)
    return Resp()


@router.post("/bot/{user_id}")
async def get_message_from_tg(
    user_id: int,
    message: MessageUser
) -> Resp:
    m_msg = Message(
        user_id=message.user_id,
        sender=Sender.user.value,
        text=message.text,
        created_at=datetime.now(timezone.utc).isoformat()
    )

    _log.info(m_msg)

    if user_id != m_msg.user_id:
        raise HTTPException(status_code=400, detail="User id not match")

    m_databese.message.insert_one(m_msg)
    _log.info(m_msg)
    asyncio.create_task(ws_chat_manager.send_message(m_msg))
    return Resp()


@router.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket,  client_id: str):
    await ws_chat_manager.connect(client_id, websocket)
    try:
        while True:
            await ws_chat_manager.receive(client_id)
    except WebSocketDisconnect:
        ws_chat_manager.disconnect(client_id)
