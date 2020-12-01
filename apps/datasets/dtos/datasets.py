""" Dataset app DTO layer
"""
from enum import Enum
from typing import Optional, List, Dict
from datetime import datetime
from pydantic import BaseModel, Field


__all__ = [
    'ColumnType',
    'DatasetInfoDTO',
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


class DatasetInfoDTO(BaseModel):
    """ transfer object for dataset file information """
    name: str
    comment: Optional[str]
    width: int
    height: int
    column_names: List[str] = Field(...)
    column_types: List[ColumnType]
    datarows: List[Dict]


class CreateDatasetDTO(DatasetInfoDTO):
    file_id: str


class DatasetDTO(DatasetInfoDTO):
    """ transfer object for dataset db models """
    id: int
    timestamp: Optional[datetime] = Field(...)

    class Config:
        orm_mode = True


class PageDTO(BaseModel):
    """ transfer object for dataset pages """
    datasets: List[DatasetDTO]
    has_next: bool
    has_prev: bool
    page_num: int
    num_pages: int
