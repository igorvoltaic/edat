import os
import csv
import datetime
from tempfile import SpooledTemporaryFile
from typing import List, Optional, Union
from uuid import UUID
from dateutil.parser import parse as dateparse
from django.core.files import File
from django.core.paginator import Paginator
from django.db.models import Q

from apps.datasets.dtos import DatasetDTO, FileDTO, UploadFileDTO, ColumnType, \
                               PageDTO
from apps.datasets.models import Dataset, DatasetFile


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
        datasets = Dataset.objects.filter(Q(name__icontains=q) |
                                          Q(comment__icontains=q))
    paginator = Paginator(datasets, 7)
    if not page_num:
        page_num = 1
    page = paginator.get_page(page_num)
    page_data = PageDTO(
        datasets=[DatasetDTO.from_orm(d) for d in page.object_list],
        has_next=page.has_next(),
        has_prev=page.has_previous(),
        page_num=page.number,
        num_pages=paginator.num_pages)
    return page_data


def handle_uploaded_file(f: SpooledTemporaryFile) -> UUID:
    """ Check if filename is unique and save uploaded file """
    uploaded_file = DatasetFile()
    uploaded_file.upload.save(f"{uploaded_file.id}.csv", f)
    return uploaded_file.id


def read_csv(filename: str,
             file_uuid: UUID,
             uploaded_file: bool = False) -> Union[FileDTO, UploadFileDTO]:
    """ Count lines, fields and read several lines
        from the file to determine datatypes
    """
    file = DatasetFile.objects.get(pk=file_uuid)
    file_obj = File(file.upload).file.read().decode()
    sniffer = csv.Sniffer()
    dialect = sniffer.sniff(file_obj)
    reader = csv.DictReader(file_obj.split('\n'), dialect=dialect)
    fieldnames = reader.fieldnames
    has_header = sniffer.has_header(file_obj)
    if not uploaded_file:
        if has_header:
            # remove header line
            line_num = sum(1 for line in file_obj.strip().split('\n')) - 1
        else:
            # if there is not header
            line_num = sum(1 for line in file_obj.strip().split('\n'))
        filename = filename[:-4]
        file_info = FileDTO(name="{}{}".format(filename[:146], ".csv"),
                            height=line_num,
                            width=len(fieldnames))
        return file_info
    else:
        file_info = UploadFileDTO(name="{}{}".format(filename[:146], ".csv"),
                                  column_names=fieldnames,
                                  column_types=[check_type(v)
                                                for v in next(reader).values()],
                                  datarows=[next(reader) for v in range(21)])
        return file_info


def save_dataset(file_uuid: UUID, dataset_info: FileDTO) -> DatasetDTO:
    """ Save new dataset to DB model """
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
