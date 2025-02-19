from datetime import datetime
import logging
import os
import aiohttp
import asyncio
import pandas as pd
from fastapi import Response
from fastapi.exceptions import HTTPException

from models.swapi_dev.people import People
from models.swapi_dev.create_file import FileInfo

_log = logging.getLogger(__name__)


class SwapiDev:
    def __init__(self, url):
        self.__url = url

    async def create_people_excel(self, resp: Response) -> FileInfo:
        _log.info("Start create excel")

        peoples_dict = await self.get_people(resp)
        peoples = self.__get_peoples_model(peoples_dict)

        df = pd.DataFrame(peoples)

        folder_path = '../static'
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)

        file_name = f"people_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.xlsx"
        path_new_file = f"{folder_path}/{file_name}"

        df.to_excel(path_new_file)

        asyncio.create_task(self.__delete_file_timeout(20, path_new_file))

        return FileInfo(path=path_new_file, name=file_name, type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

    async def __delete_file_timeout(self, timeout: int, path: str):
        await asyncio.sleep(timeout)
        if os.path.exists(path):
            os.remove(path)

    def __get_peoples_model(self, people: list[dict]) -> list[dict]:
        return [People.model_validate(person).model_dump() for person in people]

    async def get_people(self, resp: Response) -> list[dict]:
        _log.info("Start get info people")

        start_page = 1
        end_page = 2
        url = self.__url + "people"

        tasks = []
        for i in range(start_page, end_page):
            tasks.append(asyncio.create_task(
                self.__get_page_peoples(resp, url, i)))

        pages_peoples: list[list] = await asyncio.gather(*tasks)

        peoples = [people for page in pages_peoples for people in page]

        return peoples

    async def __get_page_peoples(self, resp: Response, url: str, page: int = -1):
        _log.info("Start get page people")

        if id != -1:
            url += "/?page=" + str(page)
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:

                if response.status == 200:
                    page_json: dict = await response.json()
                    peoples = page_json.get("results")

                    if peoples is None:
                        _log.error("Get info about people from json fail")
                        resp.status_code = 206
                        return []

                    return peoples
                else:
                    _log.error(
                        "Get json about people fail. Error: %s", response.text)
                    resp.status_code = 206
                    return []


swapi_dev = SwapiDev("https://swapi.dev/api/")
