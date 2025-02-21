import logging

from fastapi import APIRouter

from models.chat.tg_user import TgUser


_log = logging.getLogger(__name__)

router = APIRouter(
    prefix="/chat",
    tags=["Chat"],
)


@router.get("/")
async def get_chat():
    return {"message": "Hello from chat"}


@router.post("/user")
async def add_user(user: TgUser):
    _log.info(user.model_dump())
    return {"message": "Hello from test"}
