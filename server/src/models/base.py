from typing import Annotated, Optional

from pydantic import BaseModel, BeforeValidator, Field


PyObjectId = Annotated[str, BeforeValidator(str)]


class BaseModelInDB(BaseModel):
    id: Optional[PyObjectId] = Field(alias="_id", default=None)
    version: int
