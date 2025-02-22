from pydantic import BaseModel

from models.chat.message import MessageInDB
from models.chat.tg_user import TgUser, TgUserInDB


class Notification(BaseModel):
    type: str = "notification"
    user_id: int


class Message(BaseModel):
    type: str = "message"
    message: dict


class OpenChat(BaseModel):
    type: str = "openChat"
    history: list[dict]


class NewUser(BaseModel):
    type: str = "newUser"
    user: TgUser


class Loading(BaseModel):
    type: str = "loading"
    users: list[TgUserInDB]


class LoadingUser(BaseModel):
    type: str = "loadingUser"
    user: TgUserInDB
