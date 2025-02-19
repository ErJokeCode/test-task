from datetime import datetime
from pydantic import BaseModel, Field, ValidationInfo, field_validator


class People(BaseModel):
    name: str
    height: int | None = Field(serialization_alias='Рост')
    mass: int | None = Field(serialization_alias='Масса')
    hair_color: str
    skin_color: str
    eye_color: str
    birth_year: str
    gender: str
    homeworld: str
    films: list
    species: list
    vehicles: list
    starships: list
    created: str
    edited: str
    url: str

    @field_validator('height', 'mass', mode='before')
    def check_height(cls, v) -> int | None:
        if v is None or not str(v).isdigit():
            return None
        return int(v)
