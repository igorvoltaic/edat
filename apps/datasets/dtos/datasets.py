from datetime import datetime
from pydantic import BaseModel
from typing import Optional, List


class DatasetDTO(BaseModel):
    id: Optional[int] = ...
    name: str
    timestamp: Optional[datetime] = ...
    height: int
    width: int
    comment: str = ''

    class Config:
        orm_mode = True


class FileDTO(BaseModel):
    # id: Optional[int] = ...
    name: str
    column_names: List[str] = ...
    column_types: List[ColumnType]
    line_num: int
    column_num: int

class ColumnType(str, Enum):
    INT = "number"
    FLOAT = "float64"
