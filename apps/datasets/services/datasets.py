import os
import csv
import datetime
from tempfile import SpooledTemporaryFile
from typing import List, Optional
from django.db.models import UUIDField
from dateutil.parser import parse as dateparse
from django.conf import settings
from django.core.files import File
from django.core.files.base import ContentFile

from apps.datasets.dtos import DatasetDTO, FileDTO, ColumnType
from apps.datasets.models import Dataset, DatasetFile


def get_dataset(dataset_id: int) -> Optional[DatasetDTO]:
    """ Get selected dataset from the DB model """
    try:
        dataset = Dataset.objects.get(pk=dataset_id)
    except Dataset.DoesNotExist:
        return None
    return DatasetDTO.from_orm(dataset)


def get_file_data(dataset.file_uuid):
    file = DatasetFile.objects.get(pk=file_uuid)
    file_obj = File(file.upload).file.read().decode()
    sniffer = csv.Sniffer()
    dialect = sniffer.sniff(file_obj)
    has_header = sniffer.has_header(file_obj)
    reader = csv.DictReader(file_obj.split('\n'), dialect=dialect)
    fieldnames = reader.fieldnames
    if has_header:
        # remove header line
        line_num = sum(1 for line in file_obj.strip().split('\n')) - 1
    else:
        # if there is not header
        line_num = sum(1 for line in file_obj.strip().split('\n'))
    filename = filename[:-4]
    file_info = FileDTO(name="{}{}".format(filename[:46], ".csv"),
                        column_names=fieldnames,
                        column_types=[check_type(v) for v in next(reader).values()],
                        height=line_num,
                        width=len(fieldnames))
    return file_info



def get_all_datasets() -> List[DatasetDTO]:
    """ Get all datasets from the DB """
    datasets = Dataset.objects.all()
    return [DatasetDTO.from_orm(d) for d in datasets]


def handle_uploaded_file(f: SpooledTemporaryFile) -> UUIDField:
    """ Check if filename is unique and save uploaded file """
    uploaded_file = DatasetFile()
    uploaded_file.upload.save(f"{uploaded_file.id}.csv", f)
    return uploaded_file.id


def read_csv(filename: str, file_uuid: UUIDField) -> FileDTO:
    """ Count lines, fields and read several lines
        from the file to determine datatypes
    """
    file = DatasetFile.objects.get(pk=file_uuid)
    file_obj = File(file.upload).file.read().decode()
    sniffer = csv.Sniffer()
    dialect = sniffer.sniff(file_obj)
    has_header = sniffer.has_header(file_obj)
    reader = csv.DictReader(file_obj.split('\n'), dialect=dialect)
    fieldnames = reader.fieldnames
    if has_header:
        # remove header line
        line_num = sum(1 for line in file_obj.strip().split('\n')) - 1
    else:
        # if there is not header
        line_num = sum(1 for line in file_obj.strip().split('\n'))
    filename = filename[:-4]
    file_info = FileDTO(name="{}{}".format(filename[:46], ".csv"),
                        column_names=fieldnames,
                        column_types=[check_type(v) for v in next(reader).values()],
                        height=line_num,
                        width=len(fieldnames))
    return file_info


def save_dataset(file_uuid: UUIDField, dataset_info: FileDTO) -> DatasetDTO:
    """ Save new dataset to DB model """
    dataset = Dataset.objects.create(**dataset_info.dict())
    dataset_file = DatasetFile.objects.get(pk=file_uuid)
    dataset_file.dataset_id = dataset.id
    dataset_file.save()
    return DatasetDTO.from_orm(dataset)


def check_type(str_value):
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
