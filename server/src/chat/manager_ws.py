from datetime import datetime, timezone
import logging
from aiogram import Bot
from fastapi import WebSocket

from config import settings
from models.chat.message import Message
from database.database import m_databese
from models.base import Sender
from models.chat import resp_ws
from models.chat.tg_user import TgUser

_log = logging.getLogger(__name__)

bot = Bot(token=settings.BOT_TOKEN)


class ConnectionManager:
    def __init__(self):
        self.__active_connections: dict[str, Connect] = {}

    async def connect(self, client_id: str, websocket: WebSocket) -> None:
        _log.info("WebSocket Connection from %s", client_id)

        await websocket.accept()

        connect = Connect(websocket)
        self.__active_connections[client_id] = connect

        users = m_databese.tg_user.find(all=True)
        loading = resp_ws.Loading(users=users)
        await websocket.send_json(loading.model_dump())

    def disconnect(self, client_id: str) -> None:
        _log.info("WebSocket Disconnected from %s", client_id)

        del self.__active_connections[client_id]

    async def send_message(self, message: Message) -> None:
        _log.info("Send message to %s", message.user_id)

        m_databese.tg_user.update_one(
            {"user_id": message.user_id}, func="$inc", count_not_read=1)

        for connection in self.__active_connections.values():
            await connection.send_message(message)

    async def new_user(self, user: TgUser) -> None:
        _log.info("Send new user to %s", user.user_id)

        for connection in self.__active_connections.values():
            await connection.send_new_user(user)

    async def receive(self, client_id: str) -> None:
        _log.info("Receive message from %s", client_id)

        ws = self.__active_connections[client_id]
        await ws.receive_json()


class Connect:
    def __init__(self, web_socket: WebSocket):
        self.__web_socket = web_socket
        self.__open_chat: int | None = None

    async def send_message(self, message: Message):
        if self.__open_chat is None or \
                message.user_id != self.__open_chat:

            user_id = message.user_id
            notif = resp_ws.Notification(user_id=user_id)

            await self.__web_socket.send_json(
                notif.model_dump()
            )
        else:
            msg = resp_ws.Message(message=message.model_dump())
            await self.__web_socket.send_json(
                msg.model_dump()
            )

    async def send_history_chat(self, user_id: int):
        m_history = m_databese.message.find(
            sort={"created_at": -1}, user_id=user_id)

        history = [m.model_dump() for m in m_history]

        chat = resp_ws.OpenChat(history=history[::-1])
        await self.__web_socket.send_json(
            chat.model_dump()
        )

    async def send_new_user(self, user: TgUser):
        new_user = resp_ws.NewUser(user=user)
        await self.__web_socket.send_json(
            new_user.model_dump()
        )

    async def receive_json(self) -> None:
        data = dict(await self.__web_socket.receive_json())
        _log.info(data)

        if data.get("type") == "message" and self.__open_chat is not None and data["message"] != "":
            await bot.send_message(self.__open_chat, data["message"])

            msg = self.__message(self.__open_chat, data["message"])
            m_databese.message.insert_one(msg)

            await self.send_message(msg)

        elif data.get("type") == "openChat":
            self.__open_chat = int(data["user_id"])

            user = m_databese.tg_user.update_one(
                {"user_id": self.__open_chat}, func="$set", is_return=True, count_not_read=0
            )

            if user is not None:
                m_databese.message.update_many(
                    {"user_id": self.__open_chat}, func="$set", admin_read=True
                )

                await self.send_history_chat(self.__open_chat)

                l_user = resp_ws.LoadingUser(user=user)
                await self.__web_socket.send_json(l_user.model_dump())

    def __message(self, user_id: int, text: str) -> Message:
        m_msg = Message(
            user_id=user_id,
            sender=Sender.admin.value,
            text=text,
            admin_read=True,
            created_at=datetime.now(timezone.utc).isoformat()
        )
        return m_msg


ws_chat_manager = ConnectionManager()
