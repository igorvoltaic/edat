""" Dataset app service layer
"""
import csv
import datetime
import hashlib
import logging
import os
import shutil
from typing import Optional

from dateutil.parser import parse as dateparse
from django.core.paginator import Paginator
from django.db import transaction
from django.db.models import Q
from django.conf import settings
from pydantic import ValidationError

from apps.datasets.dtos import ColumnType, CreateDatasetDTO, DatasetDTO, \
        DatasetInfoDTO, PageDTO, CsvDialectDTO, Delimiter, Quotechar, \
        PlotDTO, CreatePlotDTO
from apps.datasets.models import Dataset, Column, CsvDialect, Plot
from helpers.csv_tools import examine_csv, count_lines, \
        handle_duplicate_fieldnames
from helpers.exceptions import FileAccessError
from helpers.file_tools import create_temporary_file, get_file_id, \
        move_tmpfile_to_media, get_tmpfile_dirpath, get_dir_path, \
        get_tmpfile_path, get_tmpfile_name
from helpers.plot_tools import render_plot, get_plot_hash


__all__ = [
    'read_dataset', 'get_all_datasets', 'read_csv',
    'create_dataset_entry', 'delete_dataset_entry', 'handle_uploaded_file',
    'delete_tmpfile', 'edit_dataset_entry', 'get_plot_img'
]


def read_dataset(
            dataset_id: int,
            dialect: Optional[CsvDialectDTO] = None
        ) -> Optional[DatasetDTO]:
    """ Get dataset object and return its file info
        to let user edit column types
        Or reread file using user-supplied delimiters
    """
    try:
        dataset = Dataset.objects.get(pk=dataset_id)  # type: ignore
        csv_dialect = dialect if dialect \
            else CsvDialectDTO.from_orm(dataset.csv_dialect)
        file_info = read_csv(dataset.name,
                             dataset.file.name,
                             csv_dialect=csv_dialect)
        file_info.comment = dataset.comment
        if not dialect:
            # In case we changed the delimiter number of columns
            # has changed as well and there is no point in reading
            # column types in the DB
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


def handle_uploaded_file(
            filename: Optional[str] = None,
            file: Optional[bytes] = None,
            file_id: Optional[str] = None,
            dialect: Optional[CsvDialectDTO] = None
        ) -> CreateDatasetDTO:
    """ Save file to Django's default temporary file location
        Read file data and return information about its contents
        Or reread information using user-supplied csv dialect
    """
    if file_id and not filename:
        tempfile = get_tmpfile_path(file_id)
        filename = get_tmpfile_name(file_id)
        if not tempfile:
            raise FileAccessError("Cannot read temporary file")
    elif file and filename:
        file_id = get_file_id()
        try:
            tempfile = create_temporary_file(filename, file_id, file)
            logging.info("Temporary file with id %s was created", file_id)
        except (FileExistsError, OSError) as e:
            raise FileAccessError("Cannot save temporary file") from e
    try:
        if file_id:
            file_info = read_csv(filename, tempfile, dialect)  # type: ignore
        else:
            file_info = read_csv(filename, tempfile)  # type: ignore
    except (ValidationError, StopIteration, ValueError) as e:
        raise FileAccessError("Invalid filename or contents") from e
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
    with open(filepath, 'r') as file:
        data = file.read()
    dialect, has_header = examine_csv(data, csv_dialect)
    if not csv_dialect:
        csv_dialect = CsvDialectDTO(
            delimiter=dialect.delimiter,
            quotechar=dialect.quotechar,
            has_header=has_header
        )
    reader = csv.DictReader(data.split('\n'), dialect=dialect)
    # return column keys in case dataset has duplicate column names
    fieldnames = reader.fieldnames
    if reader.fieldnames:
        keys = handle_duplicate_fieldnames(reader.fieldnames)
        if keys:
            reader.fieldnames = keys
    line_num = count_lines(data, has_header)
    rows_to_read = settings.SAMPLE_ROW_COUNT
    if line_num < rows_to_read:
        rows_to_read = line_num
    datarows = [next(reader) for _ in range(1, rows_to_read)]
    start_row = 0
    if csv_dialect.start_row:
        start_row = csv_dialect.start_row
    column_types = [check_type(str(v)) for v in datarows[start_row].values()]
    file_info = DatasetInfoDTO(
        name=filename,
        height=line_num,
        width=sum(1 for _ in fieldnames),
        column_names=fieldnames,
        column_types=column_types,
        datarows=datarows,
        csv_dialect=csv_dialect
    )
    return file_info


@transaction.atomic
def edit_dataset_entry(
            dataset_id: int,
            dto: DatasetDTO
        ) -> Optional[DatasetDTO]:
    """ Edit dataset Column types or dialect DB entries """
    try:
        dataset = Dataset.objects.get(pk=dataset_id)  # type: ignore
    except Dataset.DoesNotExist:  # type: ignore
        return None
    # In case we changed the delimiter number of columns was changed as well
    # and now we need to delete unnecessary columns and add new ones after that
    if Column.objects.count() != dto.width:  # type: ignore
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
    csv_dialect.start_row = dto.csv_dialect.start_row
    csv_dialect.save()
    dataset.comment = dto.comment
    dataset.save()
    return dto


@transaction.atomic
def create_dataset_entry(file_info: CreateDatasetDTO) -> Optional[DatasetDTO]:
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
            has_header=file_info.csv_dialect.has_header,
            start_row=file_info.csv_dialect.start_row
        )
        csv_dialect.save()
    except ValueError:
        logging.error(
            "Wasn't able to create a dialect db entry for dataset with id %s",
            dataset.id
        )
    file = move_tmpfile_to_media(file_info.file_id, dataset.id)
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
def delete_dataset_entry(dataset_id: int) -> Optional[DatasetInfoDTO]:
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


def get_plot_img(plot_dto: CreatePlotDTO) -> Optional[PlotDTO]:
    """ Service reads dataset file, drows plot with supplied X and Y axis info
        and returns plot file path
    """
    try:
        dataset = Dataset.objects.get(pk=plot_dto.dataset_id)  # type: ignore
        hash = get_plot_hash(plot_dto)
        plot = dataset.plots.get(checksum=hash)
        if not plot:
            plot_img_path = render_plot(
                    dataset.file.name,
                    x_axis, y_axis,
                    dataset.csv_dialect)
            plot = Plot.objects.create()  # type: ignore
    except Dataset.DoesNotExist:  # type: ignore
        return None
    return plot_img_path


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
