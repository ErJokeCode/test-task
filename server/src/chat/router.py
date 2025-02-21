import logging

from aiogram import Bot
from fastapi import APIRouter, WebSocket
from fastapi.exceptions import HTTPException

from config import settings
from models.chat.tg_user import TgUser
from models.chat.message import Message, MessageAdmin, MessageUser
from database.database import m_databese
from models.base import Resp, Sender


_log = logging.getLogger(__name__)

bot = Bot(token=settings.BOT_TOKEN)

router = APIRouter(
    prefix="/chat",
    tags=["Chat"],
)


@router.get("/")
async def get_chats():
    # страница списка чатов и вход в них
    return {"message": "Hello from chat"}


@router.post("/bot/user")
async def add_user_tg(
    user: TgUser
) -> Resp:
    m_databese.tg_user.insert_one(user)
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
        created_at=message.created_at
    )
    if user_id != m_msg.user_id:
        raise HTTPException(status_code=400, detail="User id not match")

    m_databese.message.insert_one(m_msg)
    return Resp()


@router.post("/{user_id}")
async def send_message_to_tg(
    user_id: int,
    message: MessageAdmin
) -> Resp:
    message_admin = Message(**message.model_dump())
    if user_id != message_admin.user_id:
        raise HTTPException(status_code=400, detail="User id not match")
    if message_admin.text is None:
        raise HTTPException(status_code=400, detail="Message is empty")
    msg = await bot.send_message(user_id, message_admin.text)
    _log.info(msg)
    _log.info(message_admin)
    _log.info(message_admin.model_dump_json())
    m_databese.message.insert_one(message_admin)
    return Resp()


@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    while True:
        data = await websocket.receive_text()
        await websocket.send_json({"message": data})
