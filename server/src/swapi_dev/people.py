import asyncio
from datetime import datetime
import logging
import os
from fastapi import HTTPException
import pandas as pd

from models.swapi_dev.create_file import FileInfo
from models.swapi_dev.people import People
from models.swapi_dev.people_statistic import FuncStatistic

_log = logging.getLogger(__name__)


class PeopleSD:
    def __init__(self, peoples: list[People] | pd.DataFrame) -> None:
        if isinstance(peoples, pd.DataFrame):
            df = peoples
            s_name = People.list_serialization_alias()
            err_cols = [s_name[i]
                        for i in range(len(s_name))
                        if s_name[i] != df.columns[i]]

            if len(err_cols) > 0:
                raise HTTPException(
                    status_code=400, detail=f"Excel file does not have required columns. Add cols {err_cols}")
        else:
            dict_people = [people.model_dump(
                by_alias=True) for people in peoples]
            df = pd.DataFrame(dict_people)

        if df.empty:
            raise HTTPException(
                status_code=400, detail="Excel file is empty")

        self.__df = df

    def to_excel(self, folder: str) -> FileInfo:
        file_name = f"people_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.xlsx"
        path_new_file = f"{folder}/{file_name}"

        self.__df.to_excel(path_new_file, index=False)

        asyncio.create_task(self.__delete_file_timeout(20, path_new_file))

        return FileInfo(
            path=path_new_file,
            name=file_name,
            type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

    async def __delete_file_timeout(self, timeout: int, path: str) -> None:
        await asyncio.sleep(timeout)
        if os.path.exists(path):
            os.remove(path)

    @property
    def df(self) -> pd.DataFrame:
        return self.__df.copy()

    @property
    def statistic_height(self) -> FuncStatistic:
        name_col = self.__df.columns
        s_height = self.__df[name_col[1]]

        return FuncStatistic(
            max=s_height.max(),
            min=s_height.min(),
            avg=s_height.mean()
        )

    @property
    def statistic_mass(self) -> FuncStatistic:
        name_col = self.__df.columns
        s_mass = self.__df[name_col[2]]
        return FuncStatistic(
            max=s_mass.max(),
            min=s_mass.min(),
            avg=s_mass.mean()
        )

    @property
    def popular_hair_color(self) -> str:
        name_col = self.__df.columns
        return self.__df[name_col[3]].value_counts().keys()[0]

    @property
    def unpopular_skin_color(self) -> str:
        name_col = self.__df.columns
        return self.__df[name_col[4]].value_counts().keys()[-1]

    @property
    def people_by_eye_color(self) -> dict[str, int]:
        name_col = self.__df.columns
        return {str(key): val for key, val in
                self.__df[name_col[5]].value_counts().items()}

    @property
    def highest_woman(self) -> People:
        name_col = self.__df.columns
        women = self.__df[self.__df[name_col[7]] == "female"]
        highest_woman = women.loc[women[name_col[1]].idxmax()]
        return People.create(highest_woman.to_dict())

    @property
    def oldest_man(self) -> People:
        name_col = self.__df.columns
        men = self.__df[self.__df[name_col[7]] == "male"]
        copy_men = men.copy()
        copy_men[name_col[6]] = copy_men[name_col[6]].apply(
            self.__convert_year)
        oldest_man = men.loc[copy_men[name_col[6]].idxmin()]
        return People.create(oldest_man.to_dict())

    def __convert_year(self, year: str) -> float | None:
        if pd.isna(year):
            return None
        if 'BBY' == year[-3:]:
            return -float(year[:-3])
        elif 'ABY' == year[-3:]:
            return float(year[:-3])
        return None

    @property
    def popular_homeworld(self) -> str:
        name_col = self.__df.columns
        return self.__df[name_col[8]].value_counts().keys()[0]
