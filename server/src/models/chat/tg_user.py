from models.base import BaseModelInDB, EBaseModel


class TgUser(EBaseModel):
    user_id: int
    first_name: str | None
    last_name: str | None
    username: str | None

    @classmethod
    def primary_keys(self) -> list[str]:
        return ["user_id"]


class TgUserInDB(TgUser, BaseModelInDB):
    pass
