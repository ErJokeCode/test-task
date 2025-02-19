from pydantic import BaseModel


class FileInfo(BaseModel):
    path: str
    name: str
    type: str
