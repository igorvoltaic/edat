from datetime import datetime
from pydantic import BaseModel
from typing import Optional


class DatasetDTO(BaseModel):
    id: Optional[int] = ...
    name: str
    timestamp: Optional[datetime] = ...
    height: int
    width: int
    comment: str = ''

    class Config:
        orm_mode = True
