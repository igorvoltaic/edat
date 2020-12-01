""" Dataset app service layer
"""
import csv
import datetime
import os
from typing import Optional

from dateutil.parser import parse as dateparse
from django.core.paginator import Paginator
from django.db.models import Q

from apps.datasets.dtos import ColumnType, DatasetDTO, FileDTO, PageDTO
from apps.datasets.models import Dataset, Column
from helpers import create_temporary_file, get_file_id, \
        move_tmpfile_to_media, get_tmpfilepath, count_lines, \
        is_new_file, sample_rows_count, examine_csv

__all__ = [
    'get_dataset', 'get_all_datasets', 'read_csv',
    'save_dataset', 'delete_dataset', 'handle_uploaded_file',
    'get_dataset_info', 'delete_tmpfile'
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


def get_dataset_info(dataset_id: int) -> Optional[FileDTO]:
    """ Get dataset object and return its file info
        to let user edit column types
    """
    try:
        dataset = Dataset.objects.get(pk=dataset_id)
        file_info = read_csv(dataset.name, dataset.id, dataset.file.name)
        for index, _ in enumerate(zip(
            file_info.column_names,
            file_info.column_types)
        ):
            column = Column.objects.get(
                    dataset_id=dataset_id,
                    index=index
            )
            file_info.column_names[index] = column.name
            file_info.column_types[index] = column.datatype
    except Dataset.DoesNotExist:
        return None
    return file_info


def get_all_datasets(page_num: int, query: str = None) -> PageDTO:
    """ Get all datasets from the DB """
    if not query:
        datasets = Dataset.objects.order_by("-timestamp")
    else:
        datasets = Dataset.objects.filter(
                Q(name__icontains=query) |
                Q(comment__icontains=query)
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


def read_csv(filename: str, file_id: str, filepath: str,) -> FileDTO:
    """ Count lines, fields and read several lines
        from the file to determine datatypes
    """
    file = open(filepath, 'r').read()
    dialect, has_header = examine_csv(file)
    reader = csv.DictReader(file.split('\n'), dialect=dialect)
    fieldnames = reader.fieldnames
    line_num = count_lines(file, has_header)
    rows_to_read = sample_rows_count(line_num)
    file_info = FileDTO(
        name=filename,
        file_id=file_id,
        height=line_num,
        width=sum(1 for _ in fieldnames),
        columns={
            },
        column_names=fieldnames,
        column_types=[check_type(v) for v in next(reader).values()],
        datarows=[next(reader) for _ in range(rows_to_read)],
    )
    return file_info


def edit_dataset(file_info: FileDTO) -> Optional[DatasetDTO]:
    """ Edit dataset Column DB models """
    try:
        dataset = Dataset.objects.get(pk=file_info.file_id)
    except Dataset.DoesNotExist:
        return None
    for index, data in enumerate(zip(
        file_info.column_names,
        file_info.column_types)
    ):
        column = Column.objects.get(
                dataset_id=file_info.file_id,
                index=index
        )
        column.name = data[0]
        column.datatype = data[1]
        column.save()
    return DatasetDTO.from_orm(dataset)


def save_dataset(file_info: FileDTO) -> Optional[DatasetDTO]:
    """ Save new dataset to DB model """
    if not is_new_file(file_info.file_id):
        dataset = edit_dataset(file_info)
        return dataset
    dataset = Dataset.objects.create(
            name=file_info.name,
            height=file_info.height,
            width=file_info.width,
    )
    for index, data in enumerate(zip(
        file_info.column_names,
        file_info.column_types)
    ):
        Column.objects.create(
                dataset=dataset,
                index=index,
                name=data[0],
                datatype=data[1],
            )
    file = move_tmpfile_to_media(file_info.file_id)
    dataset.file = file
    dataset.save()
    return DatasetDTO.from_orm(dataset)


def delete_dataset(dataset_id: int) -> Optional[DatasetDTO]:
    """ Delete selected dataset """
    try:
        dataset = Dataset.objects.get(pk=dataset_id)
        if dataset.file:
            if os.path.isfile(dataset.file.name):
                os.remove(dataset.file.name)
        dataset.delete()
    except Dataset.DoesNotExist:
        return None
    return DatasetDTO.from_orm(dataset)


def delete_tmpfile(file_id: str) -> Optional[str]:
    """ Delete tempfile """
    if is_new_file(file_id):
        try:
            tmpfile = get_tmpfilepath(file_id)
            os.remove(tmpfile)
        except IndexError:
            return None
    return file_id


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
