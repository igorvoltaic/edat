from enum import Enum
from datetime import datetime
from pydantic import BaseModel
from typing import Optional, List, Dict
from uuid import UUID


class ColumnType(str, Enum):
    INT = "number"
    FLOAT = "float"
    DATETIME = "datetime"
    BOOLEAN = "boolean"
    STRING = "string"


class FileDTO(BaseModel):
    name: str
    width: int
    height: int


class UploadFileDTO(BaseModel):
    name: str
    column_names: List[str] = ...
    column_types: List[ColumnType]
    datarows: List[Dict]


class DatasetDTO(BaseModel):
    id: Optional[int] = ...
    name: str
    timestamp: Optional[datetime] = ...
    height: int
    width: int
    comment: str = ''
    file_id: Optional[UUID]
    file_info: Optional[UploadFileDTO]

    class Config:
        orm_mode = True


class PageDTO(BaseModel):
    """ Returns page dto model for datasets home page """
    datasets: List[DatasetDTO]
    has_next: bool
    has_prev: bool
    page_num: int
    num_pages: int
