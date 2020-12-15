""" Dataset app DTO layer
"""
from enum import Enum
from typing import Optional, List, Dict
from datetime import datetime
from pydantic import BaseModel, Field, conint, constr


__all__ = [
    'ColumnType', 'CreateDatasetDTO', 'DatasetDTO', 'DatasetInfoDTO',
    'PageDTO', 'CsvDialectDTO', 'Delimiter', 'Quotechar'
]


class ColumnType(str, Enum):
    """ Enum class for dataset column types """
    INT = "number"
    FLOAT = "float"
    DATETIME = "datetime"
    BOOLEAN = "boolean"
    STRING = "string"


class Delimiter(str, Enum):
    COMMA = ","
    SEMICOLON = ";"
    COLON = ":"
    SPACE = " "
    TAB = "\t"


class Quotechar(str, Enum):
    SINGLE = "'"
    DOUBLE = '"'


class CsvDialectDTO(BaseModel):
    delimiter: Delimiter
    quotechar: Quotechar
    has_header: bool
    start_row: Optional[int]

    class Config:
        orm_mode = True


class DatasetInfoDTO(BaseModel):
    """ transfer object for dataset's file information """
    name: constr(min_length=5)
    comment: Optional[str]
    width: int
    height: int
    column_names: Optional[List[str]]
    column_types: Optional[List[ColumnType]]
    datarows: Optional[List[Dict]]
    csv_dialect: Optional[CsvDialectDTO]

    class Config:
        orm_mode = True


class CreateDatasetDTO(DatasetInfoDTO):
    """ transfer object for dataset create method """
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
