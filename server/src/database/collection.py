import logging
import sys
from typing import Generic, TypeVar

from models.base import BaseModelInDB, EBaseModel
from pymongo.collection import Collection
from pymongo.database import Database

_log = logging.getLogger(__name__)

I = TypeVar("I", bound=EBaseModel)
O = TypeVar("O", bound=BaseModelInDB)


class MCollect(Generic[I, O]):
    def __init__(self, db_client: Database, cls: type[I], cls_db: type[O]) -> None:
        self.__db_client = db_client

        self.__valid_class(cls, cls_db)

        name_collect = self.__name_collect(cls)
        self.__collect = db_client[name_collect]

        self.__cls = cls
        self.__cls_db = cls_db

    def __name_collect(self, cls: type[I]) -> str:
        name_collect = cls.__name__[0].lower() + cls.__name__[1:]
        name_collect = "".join(
            [ch if ch.islower() else "_" + ch.lower() for ch in name_collect])
        return name_collect

    def __valid_class(self, cls: type[I], cls_db: type[O]) -> None:
        if len(cls.primary_keys()) == 0 or len(cls_db.primary_keys()) == 0:
            _log.error(
                "Method 'primary_keys' not found in class %s or class %s", cls.__name__, cls_db.__name__)
            sys.exit()

    @property
    def collect(self) -> Collection:
        return self.__collect

    def find_one(self, *primary_keys, **kwargs) -> O | None:
        if len(primary_keys) == len(self.__cls.primary_keys()):
            kwargs = dict(zip(self.__cls.primary_keys(), primary_keys))
        val = self.__collect.find_one(kwargs)
        if val is None:
            return None
        return self.__cls_db.model_validate(val)

    def insert_one(self, obj: I, is_find: bool = False) -> O | None:
        id = self.__collect.insert_one(
            obj.model_dump(by_alias=True)).inserted_id
        if is_find:
            val = self.find_one(_id=id)
            if val is None:
                return None
            return self.__cls_db.model_validate(val)
        return None
