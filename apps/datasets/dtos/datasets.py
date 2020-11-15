from datetime import datetime
from pydantic import BaseModel
from typing import List


class DatasetDTO(BaseModel):
    id: int = None
    name: str
    timestamp: datetime = None
    height: int
    width: int
    comment: str = ''

    class Config:
        orm_mode = True


class DatasetDTOList(BaseModel):
    __root__: List[DatasetDTO]
