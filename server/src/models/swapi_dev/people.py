from fastapi import HTTPException
import pandas as pd
from pydantic import BaseModel, Field, field_validator


class People(BaseModel):
    name: str = Field(serialization_alias="Имя")
    height: int | None = Field(serialization_alias="Рост")
    mass: int | None = Field(serialization_alias="Масса")
    hair_color: str | None = Field(serialization_alias="Цвет волос")
    skin_color: str | None = Field(serialization_alias="Цвет кожи")
    eye_color: str | None = Field(serialization_alias="Цвет глаз")
    birth_year: str | None = Field(serialization_alias="Год рождения")
    gender: str | None = Field(serialization_alias="Пол")
    homeworld: str = Field(serialization_alias="Домашний мир")
    films: list = Field(serialization_alias="Фильмы")
    species: list = Field(serialization_alias="Разновидность")
    vehicles: list = Field(serialization_alias="Транспорт")
    starships: list = Field(serialization_alias="Космические корабли")
    created: str = Field(serialization_alias="Дата создания")
    edited: str = Field(serialization_alias="Дата редактирования")
    url: str = Field(serialization_alias="Ссылка")

    @field_validator("height", "mass", mode="before")
    def check_integer(cls, v) -> int | None:
        if v is None or not str(v).isdigit():
            return None
        return int(v)

    @field_validator("hair_color", "skin_color", "eye_color",
                     "birth_year", "gender", mode="before")
    def check_string(cls, v) -> str | None:
        if v is None or v in ["n/a", "unknown", "none"]:
            return None
        return v

    @classmethod
    def create(cls, item: dict) -> "People":
        s_name = cls.list_serialization_alias()
        keys = item.keys()
        for name in s_name:
            if name not in keys:
                raise HTTPException(
                    status_code=400,
                    detail=f"Dict has not key {name}. All keys {keys}")

        resp_cls = cls(
            name=item["Имя"],
            height=None if pd.isna(item["Рост"]) else int(item["Рост"]),
            mass=None if pd.isna(item["Масса"]) else int(item["Масса"]),
            hair_color=None if pd.isna(
                item["Цвет волос"]) else str(item["Цвет волос"]),
            skin_color=None if pd.isna(
                item["Цвет кожи"]) else str(item["Цвет кожи"]),
            eye_color=None if pd.isna(
                item["Цвет глаз"]) else str(item["Цвет глаз"]),
            birth_year=None if pd.isna(
                item["Год рождения"]) else str(item["Год рождения"]),
            gender=None if pd.isna(item["Пол"]) else str(item["Пол"]),
            homeworld=item["Домашний мир"],
            films=[f for f in str(item["Фильмы"])[1:-1].split(", ")],
            species=[r for r in str(item["Разновидность"])[1:-1].split(", ")],
            vehicles=[v for v in str(item["Транспорт"])[1:-1].split(", ")],
            starships=[s for s in str(item["Космические корабли"])[
                1:-1].split(", ")],
            created=item["Дата создания"],
            edited=item["Дата редактирования"],
            url=item["Ссылка"]
        )
        return resp_cls

    @staticmethod
    def list_serialization_alias():
        return [
            "Имя", "Рост", "Масса",
            "Цвет волос", "Цвет кожи",
            "Цвет глаз", "Год рождения",
            "Пол", "Домашний мир",
            "Фильмы", "Разновидность",
            "Транспорт", "Космические корабли",
            "Дата создания", "Дата редактирования",
            "Ссылка"
        ]
