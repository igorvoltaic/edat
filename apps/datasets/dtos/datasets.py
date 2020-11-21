from enum import Enum
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, UUID4


class DatasetDTO(BaseModel):
    id: Optional[int] = ...
    name: str
    timestamp: Optional[datetime] = ...
    height: int
    width: int
    comment: str = ''

    class Config:
        orm_mode = True


class ColumnType(str, Enum):
    INT = "number"
    FLOAT = "float"
    DATETIME = "datetime"
    BOOLEAN = "boolean"
    STRING = "string"


class FileDTO(BaseModel):
    name: str
    column_names: List[str] = ...
    column_types: List[ColumnType]
    width: int
    height: int
