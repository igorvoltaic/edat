""" Dataset app DTO layer
"""
from enum import Enum
from typing import Optional, List, Dict
from uuid import UUID
from datetime import datetime
from pydantic import BaseModel, Field


__all__ = [
    'ColumnType',
    'FileDTO',
    'DatasetDTO',
    'PageDTO'
]


class ColumnType(str, Enum):
    """ Enum class which returns dataset column types """
    INT = "number"
    FLOAT = "float"
    DATETIME = "datetime"
    BOOLEAN = "boolean"
    STRING = "string"


class FileDTO(BaseModel):
    """ transfer object for dataset file information """
    name: str
    file_id: str
    width: int
    height: int
    comment: Optional[str]
    column_names: List[str] = Field(...)
    column_types: List[ColumnType]
    datarows: List[Dict]


class DatasetDTO(BaseModel):
    """ transfer object for dataset db models """
    id: Optional[int] = Field(...)
    name: str
    timestamp: Optional[datetime] = Field(...)
    height: int
    width: int
    comment: str = ''
    file_id: Optional[UUID]
    file_info: Optional[FileDTO]

    class Config:
        orm_mode = True


class PageDTO(BaseModel):
    """ transfer object for dataset pages """
    datasets: List[DatasetDTO]
    has_next: bool
    has_prev: bool
    page_num: int
    num_pages: int
