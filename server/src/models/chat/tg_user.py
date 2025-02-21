from pydantic import BaseModel

from models.base import BaseModelInDB


class TgUser(BaseModel):
    user_id: str | int
    first_name: str
    last_name: str
    username: str


class TgUserInDB(TgUser, BaseModelInDB):
    pass
