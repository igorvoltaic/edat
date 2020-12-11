""" Dataset app service layer
"""
import csv
import datetime
import logging
import os
import shutil
from typing import Optional

from dateutil.parser import parse as dateparse
from django.core.paginator import Paginator
from django.db import transaction
from django.db.models import Q
from django.conf import settings
from fastapi import HTTPException
from pydantic import ValidationError

from apps.datasets.dtos import ColumnType, CreateDatasetDTO, DatasetDTO, \
        DatasetInfoDTO, PageDTO, CsvDialectDTO, Delimiter, Quotechar
from apps.datasets.models import Dataset, Column, CsvDialect
from helpers.file_tools import create_temporary_file, get_file_id, \
        move_tmpfile_to_media, get_tmpfile_dirpath, get_dir_path, \
        get_tmpfile_path
from helpers.csv_tools import sample_rows_count, examine_csv, count_lines


__all__ = [
    'get_dataset', 'get_all_datasets', 'read_csv',
    'create_dataset', 'delete_dataset', 'handle_uploaded_file',
    'delete_tmpfile', 'edit_dataset', 'reread_uploaded_file',
    'reread_dataset_file'
]


def get_dataset(dataset_id: int) -> Optional[DatasetDTO]:
    """ Get dataset object and return its file info
        to let user edit column types
    """
    try:
        dataset = Dataset.objects.get(pk=dataset_id)  # type: ignore
        csv_dialect = CsvDialectDTO.from_orm(dataset.csv_dialect)
        file_info = read_csv(dataset.name,
                             dataset.file.name,
                             csv_dialect=csv_dialect)
        file_info.comment = dataset.comment
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
            timestamp=dataset.timestamp,
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


def reread_dataset_file(dto: DatasetDTO) -> Optional[DatasetDTO]:
    try:
        dataset = Dataset.objects.get(pk=dto.id)  # type: ignore
        file_info = read_csv(dataset.name,
                             dataset.file.name,
                             csv_dialect=dto.csv_dialect)
        file_info.comment = dataset.comment
    except Dataset.DoesNotExist:  # type: ignore
        return None
    return DatasetDTO(
            **file_info.dict(),
            id=dataset.id,
            timestamp=dataset.timestamp,
        )


def reread_uploaded_file(file_info: CreateDatasetDTO) -> CreateDatasetDTO:
    file_id = file_info.file_id
    filename = file_info.name
    tempfile = get_tmpfile_path(file_id)
    if not tempfile:
        raise HTTPException(
                status_code=503,
                detail="Cannot read temporary file"
        )
    try:
        updated_info = read_csv(filename, tempfile, file_info.csv_dialect)
    except (ValidationError, StopIteration, ValueError) as invalid_file:
        raise HTTPException(
                status_code=400,
                detail="Invalid filename or contents"
        ) from invalid_file
    create_dto = CreateDatasetDTO(**updated_info.dict(), file_id=file_id)
    return create_dto


def handle_uploaded_file(filename: str, file: bytes) -> CreateDatasetDTO:
    """ Save file to Django's default temporary file location """
    file_id = get_file_id()
    try:
        tempfile = create_temporary_file(filename, file_id, file)
    except (FileExistsError, OSError):
        raise HTTPException(
                status_code=503,
                detail="Cannot save temporary file"
        )
    logging.info("Temporary file with id %s was created", file_id)
    try:
        file_info = read_csv(filename, tempfile)
    except (ValidationError, StopIteration, ValueError) as invalid_file:
        raise HTTPException(
                status_code=400,
                detail="Invalid filename or contents"
        ) from invalid_file
    create_dto = CreateDatasetDTO(**file_info.dict(), file_id=file_id)
    return create_dto


def read_csv(
            filename: str,
            filepath: str,
            csv_dialect: CsvDialectDTO = None
        ) -> DatasetInfoDTO:
    """ Count lines, fields and read several lines
        from the file to determine datatypes
    """
    file = open(filepath, 'r').read()
    dialect, has_header = examine_csv(file, csv_dialect)
    if not csv_dialect:
        csv_dialect = CsvDialectDTO(
            delimiter=dialect.delimiter,
            quotechar=dialect.quotechar,
            has_header=has_header
        )
    reader = csv.DictReader(file.split('\n'), dialect=dialect)
    fieldnames = reader.fieldnames
    line_num = count_lines(file, has_header)
    rows_to_read = sample_rows_count(line_num)
    file_info = DatasetInfoDTO(
        name=filename,
        height=line_num,
        width=sum(1 for _ in fieldnames),
        column_names=fieldnames,
        column_types=[check_type(str(v)) for v in next(reader).values()],
        datarows=[next(reader) for _ in range(rows_to_read)],
        csv_dialect=csv_dialect
    )
    return file_info


@transaction.atomic
def edit_dataset(dataset_id: int, dto: DatasetDTO) -> Optional[DatasetDTO]:
    """ Edit dataset Column DB models """
    try:
        dataset = Dataset.objects.get(pk=dataset_id)  # type: ignore
    except Dataset.DoesNotExist:  # type: ignore
        return None
    # In case we changed the delimiter number of columns was changed as well
    # and now we need to delete unnecessary columns and add new ones after that
    if Column.objects.count() == dto.width:  # type: ignore
        Column.objects.all().delete()  # type: ignore
        for index, data in enumerate(zip(  # type: ignore
            dto.column_names,
            dto.column_types)
        ):
            Column.objects.create(  # type: ignore
                    dataset=dataset,
                    index=index,
                    name=data[0],
                    datatype=ColumnType(data[1]),
                )
    else:
        for index, col_type in enumerate(dto.column_types):  # type: ignore
            column = Column.objects.get(  # type: ignore
                    dataset_id=dataset.id,
                    index=index
            )
            column.datatype = col_type
            column.save()
    csv_dialect = CsvDialect.objects.get(  # type: ignore
        dataset_id=dataset.id
    )
    csv_dialect.delimiter = Delimiter(dto.csv_dialect.delimiter)
    csv_dialect.quotechar = Quotechar(dto.csv_dialect.quotechar)
    csv_dialect.has_header = dto.csv_dialect.has_header
    csv_dialect.save()
    dataset.comment = dto.comment
    dataset.save()
    return dto


@transaction.atomic
def create_dataset(file_info: CreateDatasetDTO) -> Optional[DatasetDTO]:
    """ Save new dataset to DB model """
    dataset = Dataset.objects.create(  # type: ignore
            name=file_info.name,
            height=file_info.height,
            width=file_info.width,
            comment=file_info.comment
    )
    for index, data in enumerate(zip(  # type: ignore
        file_info.column_names,
        file_info.column_types)
    ):
        Column.objects.create(  # type: ignore
                dataset=dataset,
                index=index,
                name=data[0],
                datatype=ColumnType(data[1]),
            )
    try:
        csv_dialect = CsvDialect.objects.create(  # type: ignore
            dataset_id=dataset.id,
            delimiter=Delimiter(file_info.csv_dialect.delimiter),
            quotechar=Quotechar(file_info.csv_dialect.quotechar),
            has_header=file_info.csv_dialect.has_header
        )
        csv_dialect.save()
    except ValueError:
        pass
    file = move_tmpfile_to_media(file_info.file_id)
    if not file:
        return None
    logging.info("Temporary file with id %s was moved to media",
                 file_info.file_id)
    dataset.file = file
    dataset.save()
    return DatasetDTO(
            id=dataset.id,
            name=dataset.name,
            timestamp=dataset.timestamp,
            width=dataset.width,
            height=dataset.height,
            comment=dataset.comment,
            column_names=file_info.column_names,
            column_types=file_info.column_types,
        )


@transaction.atomic
def delete_dataset(dataset_id: int) -> Optional[DatasetInfoDTO]:
    """ Delete selected dataset """
    try:
        dataset = Dataset.objects.get(pk=dataset_id)  # type: ignore
        dataset.delete()
        if dataset.file:
            if os.path.isfile(dataset.file.name):
                file_dir = get_dir_path(dataset.file.name)
                shutil.rmtree(file_dir)
                logging.info("Dataset file was deleted")
    except Dataset.DoesNotExist:  # type: ignore
        return None
    return DatasetInfoDTO.from_orm(dataset)


def delete_tmpfile(file_id: str) -> Optional[str]:
    """ Delete tempfile """
    tmp_file_dir = get_tmpfile_dirpath(file_id)
    if tmp_file_dir:
        shutil.rmtree(tmp_file_dir)
        logging.info("Temporary file with id %s was deleted", file_id)
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
