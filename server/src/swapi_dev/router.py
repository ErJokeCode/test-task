import logging

from fastapi import APIRouter, Response
from fastapi.responses import FileResponse

from swapi_dev.swapi_dev import swapi_dev


_log = logging.getLogger(__name__)

router = APIRouter(
    prefix="/swapi_dev",
    tags=["Swapi dev"],
)


@router.get("/file")
async def get_excel(response: Response):

    file_info = await swapi_dev.create_people_excel(response)

    return FileResponse(
        path=file_info.path,
        media_type=file_info.type,
        filename=file_info.name
    )
