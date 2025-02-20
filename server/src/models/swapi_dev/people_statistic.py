from pydantic import BaseModel

from models.swapi_dev.people import People


class PeopleStatistic(BaseModel):
    height: "FuncStatistic"
    mass: "FuncStatistic"
    popular_hair_color: str
    unpopular_skin_color: str
    people_by_eye_color: dict[str, int]
    highest_woman: People
    oldest_man: People
    popular_homeworld: str


class FuncStatistic(BaseModel):
    max: float
    min: float
    avg: float
