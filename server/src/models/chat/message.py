from datetime import datetime, timezone

from pydantic import BaseModel, ConfigDict, field_validator
from models.base import BaseModelInDB, EBaseModel, Sender


class Message(EBaseModel):
    user_id: int
    sender: str = Sender.admin.value
    text: str | None
    created_at: datetime = datetime.now(timezone.utc)

    @classmethod
    def primary_keys(self) -> list[str]:
        return ["user_id"]

    model_config = ConfigDict(use_enum_values=True)


class MessageAdmin(BaseModel):
    user_id: int
    text: str | None
    created_at: datetime = datetime.now(timezone.utc)


class MessageUser(BaseModel):
    user_id: int
    text: str | None
    created_at: datetime = datetime.now(timezone.utc)


class MessageInDB(Message, BaseModelInDB):
    pass
