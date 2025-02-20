from datetime import datetime
import logging
import os
import aiohttp
import asyncio
import pandas as pd
from fastapi import Response, UploadFile

from models.swapi_dev.people import People
from models.swapi_dev.create_file import FileInfo
from models.swapi_dev.people_statistic import PeopleStatistic
from swapi_dev.people import PeopleSD

_log = logging.getLogger(__name__)


class SwapiDev:
    def __init__(self, url: str, temp_folder: str):
        self.__url = url
        self.__temp_folder = temp_folder

        if not os.path.exists(self.__temp_folder):
            os.makedirs(self.__temp_folder)

    async def peoples_excel(self, resp: Response) -> FileInfo:
        _log.info("Start create excel")

        md_peoples = await self.peoples(resp)
        file_people = PeopleSD(md_peoples)

        return file_people.to_excel(self.__temp_folder)

    async def peoples(self, resp: Response = Response()) -> list[People]:
        _log.info("Start get info people")

        url = self.__url + "people"
        start_page = 1
        end_page = await self.__count_page(url) + start_page

        tasks = []
        for i in range(start_page, end_page):
            tasks.append(asyncio.create_task(
                self.__get_page_peoples(resp, url, i)))

        pages_peoples: list[list] = await asyncio.gather(*tasks)

        peoples = [People(**people)
                   for page in pages_peoples for people in page]

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

    async def __count_page(self, url: str) -> int:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status == 200:
                    page_json: dict = await response.json()
                    count = page_json.get("count")
                    one_page = page_json.get("results")

                    if one_page == None or count == None:
                        _log.warning(
                            "Count page fail one_page or count is None. Dict: %s", page_json)
                        return 1
                    len_one_page = len(one_page)

                    return (count // len_one_page) + int(count % len_one_page != 0)
                else:
                    _log.error(
                        "Get json about people fail. Error: %s", response.text)
                    return 1

    async def stitistic(self, file: UploadFile | None = None) -> PeopleStatistic:
        _log.info("Get stitistics")

        if file is None:
            peoples_dict = await self.peoples()
            df = pd.DataFrame(peoples_dict)
        else:
            excel = pd.ExcelFile(await file.read())
            df = pd.read_excel(excel)

        file_people = PeopleSD(df)

        return PeopleStatistic(
            height=file_people.statistic_height,
            mass=file_people.statistic_mass,
            popular_hair_color=file_people.popular_hair_color,
            unpopular_skin_color=file_people.unpopular_skin_color,
            people_by_eye_color=file_people.people_by_eye_color,
            highest_woman=file_people.highest_woman,
            oldest_man=file_people.oldest_man,
            popular_homeworld=file_people.popular_homeworld
        )


swapi_dev = SwapiDev("https://swapi.dev/api/", "temp")
