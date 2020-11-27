import os
import csv
import datetime

from typing import Optional
from dateutil.parser import parse as dateparse

from django.core.paginator import Paginator
from django.db.models import Q

from apps.datasets.dtos import DatasetDTO, FileDTO, ColumnType, PageDTO
from apps.datasets.models import Dataset, DatasetFile

from helpers.create_temporary_file import create_temporary_file
from helpers.get_tmpfilepath import get_tmpfilepath
from helpers.get_file_id import get_file_id


__all__ = [
    'get_dataset',
    'get_all_datasets',
    'read_csv',
    'create_new_dataset',
    'delete_dataset',
    'handle_uploaded_file'
]


def get_dataset(dataset_id: int) -> Optional[DatasetDTO]:
    """ Get selected dataset from the DB model """
    try:
        dataset = Dataset.objects.get(pk=dataset_id)
        dto = DatasetDTO.from_orm(dataset)
        dto.file_id = dataset.file.id
    except Dataset.DoesNotExist:
        return None
    return dto


def get_all_datasets(page_num: int, q: str = None) -> PageDTO:
    """ Get all datasets from the DB """
    if not q:
        datasets = Dataset.objects.order_by("-timestamp")
    else:
        datasets = Dataset.objects.filter(
                Q(name__icontains=q) |
                Q(comment__icontains=q)
        )
    paginator = Paginator(datasets, 7)
    if not page_num:
        page_num = 1
    page = paginator.get_page(page_num)
    page_data = PageDTO(
        datasets=[DatasetDTO.from_orm(d) for d in page.object_list],
        has_next=page.has_next(),
        has_prev=page.has_previous(),
        page_num=page.number,
        num_pages=paginator.num_pages
    )
    return page_data


def handle_uploaded_file(filename: str, file: bytes) -> FileDTO:
    """ Save file to Django's default temporary file location """
    file_id = get_file_id()
    tempfile = create_temporary_file(filename, file_id, file)
    file_info = read_csv(filename, file_id, tempfile)
    return file_info


def read_csv(filename: str, filepath: str,) -> FileDTO:
    """ Count lines, fields and read several lines
        from the file to determine datatypes
    """
    file = open(filepath, 'r').read()
    sniffer = csv.Sniffer()
    dialect = sniffer.sniff(file)
    reader = csv.DictReader(file.split('\n'), dialect=dialect)
    fieldnames = reader.fieldnames
    has_header = sniffer.has_header(file)
    if has_header:
        # remove header line
        line_num = sum(1 for _ in file.strip().split('\n')) - 1
    else:
        # if there is not header
        line_num = sum(1 for _ in file.strip().split('\n'))
    file_info = FileDTO(
            name_info=filename,
            tmpfile=get_tmpfilename(filepath),
            height=line_num,
            width=sum(1 for _ in fieldnames),
            column_names=fieldnames,
            column_types=[check_type(v) for v in next(reader).values()],
            datarows=[next(reader) for _ in range(21)],
    )
    return file_info


def create_new_dataset(file_info: FileDTO) -> DatasetDTO:
    """ Save new dataset to DB model """
    orig_filename = get_tmpfilename(tempfile)
    tempfilepath = get_tmpfilepath(tempfile)
    file_info.column_types = [ColumnType(t) for t in column_types]
    file_info.column_names = column_names
    dataset = Dataset.objects.create(**dataset_info.dict())
    dataset_file = DatasetFile.objects.get(pk=file_uuid)
    dataset_file.dataset_id = dataset.id
    dataset_file.save()
    return DatasetDTO.from_orm(dataset)


def check_type(str_value: str) -> ColumnType:
    """ Try to determine datatype from a string """
    try:
        if isinstance(int(str_value), int):
            return ColumnType.INT
    except ValueError:
        pass
    try:
        if isinstance(float(str_value), float):
            return ColumnType.FLOAT
    except ValueError:
        pass
    try:
        if isinstance(dateparse(str_value), datetime.date):
            return ColumnType.DATETIME
    except ValueError:
        pass
    try:
        if str_value.lower() == "true" or str_value.lower() == "false":
            return ColumnType.BOOLEAN
    except ValueError:
        pass
    return ColumnType.STRING


def delete_dataset(dataset_id: int) -> Optional[DatasetDTO]:
    """ Delete selected dataset """
    try:
        dataset = Dataset.objects.get(pk=dataset_id)
        if dataset.file:
            if os.path.isfile(dataset.file.upload.path):
                os.remove(dataset.file.upload.path)
        dataset.delete()
    except Dataset.DoesNotExist:
        return None
    return DatasetDTO.from_orm(dataset)
