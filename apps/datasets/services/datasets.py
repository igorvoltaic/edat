# import pandas as pd
import os
import csv
import datetime
from io import StringIO
from typing import List, Optional
from dateutil.parser import parse as dateparse
from django.conf import settings
from uuid import uuid4

from apps.datasets.dtos import DatasetDTO, FileDTO, ColumnType
from apps.datasets.models import Dataset, DatasetFile


def get_dataset(dataset_id: int) -> Optional[DatasetDTO]:
    """ Get selected dataset from the DB model """
    try:
        dataset = Dataset.objects.get(pk=dataset_id)
    except Dataset.DoesNotExist:
        return None
    return DatasetDTO.from_orm(dataset)


def get_all_datasets() -> List[DatasetDTO]:
    """ Get all datasets from the DB """
    datasets = Dataset.objects.all()
    return [DatasetDTO.from_orm(d) for d in datasets]


def uniq_filename(path: str, file_path: str) -> str:
    """ Check if uuid filename is uniq """
    if not os.path.isfile(file_path):
        return f"{file_path}.csv"
    uniq_filename(path, str(uuid4()))


def handle_uploaded_file(f: bytes) -> str:
    """ Check if filename is unique and save uploaded file """
    path = os.path.join(os.path.abspath(settings.MEDIA_ROOT),
                        "apps/datasets/uploads/")
    file_path = uniq_filename(path, os.path.join(path, str(uuid4())))
    with open(file_path, 'wb+') as destination:
        destination.write(f)
    return file_path


def save_file(csvfile) -> int:
    dataset_file = DatasetFile(upload=csvfile)
    dataset_file.save()
    return dataset_file.id


def read_csv(filename, file_path) -> FileDTO:
    """ Count lines, fields and read several lines
        from the file to determine datatypes
    """
    sniffer = csv.Sniffer()
    f = open(file_path).read()
    dialect = sniffer.sniff(f)
    has_header = sniffer.has_header(f)
    reader = csv.DictReader(f.split('\n'), dialect=dialect)
    fieldnames = reader.fieldnames
    if has_header:
        # remove header line
        line_num = sum(1 for line in f.strip().split('\n')) - 1
    else:
        # if there is not header
        line_num = sum(1 for line in f.strip().split('\n'))
    file_info = FileDTO(name=filename,
                        column_names=fieldnames,
                        column_types=[ColumnType(check_type(v))
                                      for v in next(reader).values()],
                        line_num=line_num,
                        column_num=len(tuple(fieldnames)))
    return file_info


def save_dataset(dataset_info: DatasetDTO) -> DatasetDTO:
    """ Save new dataset to DB model """
    dataset = Dataset.objects.create(**dataset_info.dict())
    return DatasetDTO.from_orm(dataset)


def check_type(str_value):
    """ Try to determine datatype from a string """
    try:
        if isinstance(int(str_value), int):
            return "number"
    except ValueError:
        pass
    try:
        if isinstance(float(str_value), float):
            return "float"
    except ValueError:
        pass
    try:
        if isinstance(dateparse(str_value), datetime.date):
            return "datetime"
    except ValueError:
        pass
    try:
        if str_value.lower() == "true" or str_value.lower() == "false":
            return "boolean"
    except ValueError:
        pass
    return "string"
