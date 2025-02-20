import logging

from fastapi import APIRouter, Response, UploadFile
from fastapi.responses import FileResponse

from models.swapi_dev.people_statistic import PeopleStatistic
from models.swapi_dev.people import People
from swapi_dev.swapi_dev import swapi_dev


_log = logging.getLogger(__name__)

router = APIRouter(
    prefix="/swapi_dev",
    tags=["Swapi dev"],
)


@router.get("/people")
async def get_peoples(resp: Response) -> list[People]:
    return await swapi_dev.peoples(resp)


@router.get("/people/file")
async def get_excel(
    resp: Response
) -> FileResponse:

    file_info = await swapi_dev.peoples_excel(resp)

    return FileResponse(
        path=file_info.path,
        media_type=file_info.type,
        filename=file_info.name
    )


@router.post("/people/file/statistic")
async def get_excel_static(
    file: UploadFile | None = None
) -> PeopleStatistic:
    return await swapi_dev.stitistic(file)
