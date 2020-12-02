""" Dataset app service layer
"""
import csv
import datetime
import os
import shutil
from typing import Optional

from dateutil.parser import parse as dateparse
from django.core.paginator import Paginator
from django.db.models import Q
from django.conf import settings

from apps.datasets.dtos import ColumnType, CreateDatasetDTO, DatasetDTO, \
        DatasetInfoDTO, PageDTO
from apps.datasets.models import Dataset, Column
from helpers import create_temporary_file, get_file_id, \
        move_tmpfile_to_media, get_tmpfilepath, count_lines, \
        sample_rows_count, examine_csv, get_dir_path

__all__ = [
    'get_dataset', 'get_all_datasets', 'read_csv',
    'create_dataset', 'delete_dataset', 'handle_uploaded_file',
    'delete_tmpfile', 'edit_dataset'
]


def get_dataset(dataset_id: int) -> Optional[DatasetDTO]:
    """ Get dataset object and return its file info
        to let user edit column types
    """
    try:
        dataset = Dataset.objects.get(pk=dataset_id)  # type: ignore
        file_info = read_csv(dataset.name, dataset.file.name)
        for index, _ in enumerate(zip(  # type: ignore
            file_info.column_names,
            file_info.column_types)
        ):
            column = Column.objects.get(  # type: ignore
                    dataset_id=dataset_id,
                    index=index
            )
            file_info.column_names[index] = column.name
            file_info.column_types[index] = column.datatype
    except Dataset.DoesNotExist:  # type: ignore
        return None
    return DatasetDTO(
            **file_info.dict(),
            id=dataset.id,
            timestamp=dataset.timestamp
        )


def get_all_datasets(page_num: int, query: str = None) -> PageDTO:
    """ Get all datasets from the DB """
    if not query:
        datasets = Dataset.objects.order_by("-timestamp")  # type: ignore
    else:
        datasets = Dataset.objects.filter(  # type: ignore
                Q(name__icontains=query) |
                Q(comment__icontains=query)
        )
    paginator = Paginator(datasets, settings.ITEMS_PER_PAGE)
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


def handle_uploaded_file(filename: str, file: bytes) -> CreateDatasetDTO:
    """ Save file to Django's default temporary file location """
    file_id = get_file_id()
    tempfile = create_temporary_file(filename, file_id, file)
    file_info = read_csv(filename, tempfile)
    create_dto = CreateDatasetDTO(**file_info.dict(), file_id=file_id)
    return create_dto


def read_csv(filename: str, filepath: str,) -> DatasetInfoDTO:
    """ Count lines, fields and read several lines
        from the file to determine datatypes
    """
    file = open(filepath, 'r').read()
    dialect, has_header = examine_csv(file)
    reader = csv.DictReader(file.split('\n'), dialect=dialect)
    fieldnames = reader.fieldnames
    line_num = count_lines(file, has_header)
    rows_to_read = sample_rows_count(line_num)
    file_info = DatasetInfoDTO(
        name=filename,
        height=line_num,
        width=sum(1 for _ in fieldnames),
        column_names=fieldnames,
        column_types=[check_type(v) for v in next(reader).values()],
        datarows=[next(reader) for _ in range(rows_to_read)],
    )
    return file_info


def edit_dataset(dataset_id: int, dto: DatasetDTO) -> Optional[DatasetDTO]:
    """ Edit dataset Column DB models """
    try:
        dataset = Dataset.objects.get(pk=dataset_id)  # type: ignore
    except Dataset.DoesNotExist:  # type: ignore
        return None
    for index, type in enumerate(dto.column_types):  # type: ignore
        column = Column.objects.get(  # type: ignore
                dataset_id=dataset.id,
                index=index
        )
        column.datatype = type
        column.save()
    return dto


def create_dataset(file_info: CreateDatasetDTO) -> Optional[DatasetDTO]:
    """ Save new dataset to DB model """
    dataset = Dataset.objects.create(  # type: ignore
            name=file_info.name,
            height=file_info.height,
            width=file_info.width,
    )
    for index, data in enumerate(zip(  # type: ignore
        file_info.column_names,
        file_info.column_types)
    ):
        Column.objects.create(  # type: ignore
                dataset=dataset,
                index=index,
                name=data[0],
                datatype=data[1],
            )
    file = move_tmpfile_to_media(file_info.file_id)
    if not file:
        return None
    dataset.file = file
    dataset.save()
    return DatasetDTO(
            id=dataset.id,
            name=dataset.name,
            timestamp=dataset.timestamp,
            width=dataset.width,
            height=dataset.height,
            column_names=file_info.column_names,
            column_types=file_info.column_types,
        )


def delete_dataset(dataset_id: int) -> Optional[DatasetInfoDTO]:
    """ Delete selected dataset """
    try:
        dataset = Dataset.objects.get(pk=dataset_id)  # type: ignore
        dataset.delete()
        if dataset.file:
            if os.path.isfile(dataset.file.name):
                file_dir = get_dir_path(dataset.file.name)
                shutil.rmtree(file_dir)
    except Dataset.DoesNotExist:  # type: ignore
        return None
    return DatasetInfoDTO.from_orm(dataset)


def delete_tmpfile(file_id: str) -> Optional[str]:
    """ Delete tempfile """
    tmp_file_dir = get_tmpfilepath(file_id)
    if tmp_file_dir:
        shutil.rmtree(tmp_file_dir)
        return file_id
    return None


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
