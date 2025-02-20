import logging

from fastapi import APIRouter


_log = logging.getLogger(__name__)

router = APIRouter(
    prefix="/chat",
    tags=["Chat"],
)


@router.get("/")
async def get_chat():
    return {"message": "Hello from chat"}
