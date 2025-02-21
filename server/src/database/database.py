import logging
import sys
from typing import Generic, TypeVar

from config import settings
from models.base import BaseModelInDB, EBaseModel
from pymongo import MongoClient
from pymongo.collection import Collection
from pymongo.database import Database

from database.collection import MCollect
from models.chat.tg_user import TgUser, TgUserInDB
from models.chat.message import Message, MessageInDB

_log = logging.getLogger(__name__)


class MDataBase():
    def __init__(self, host: str, port: int, name_db: str):
        self.__db: Database = MongoClient(
            host=host, port=port)[name_db]

        self.tg_user = MCollect(self.__db, TgUser, TgUserInDB)
        self.message = MCollect(self.__db, Message, MessageInDB)


m_databese = MDataBase(
    settings.DB_HOST,
    settings.DB_PORT,
    settings.DB_NAME
)
