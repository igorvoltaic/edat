""" Helper funciton to get line count of csv file
"""
import csv
import datetime
from typing import Tuple, Type, Optional, List, Sequence

from dateutil.parser import parse as dateparse
from django.conf import settings

from apps.datasets.dtos import CsvDialectDTO, DatasetInfoDTO, ColumnType
from helpers.exceptions import FileAccessError


def count_lines(file: str, has_header: bool) -> int:
    """ Return number of lines in file """
    if has_header:
        # remove header line
        line_num = sum(1 for _ in file.strip().split('\n')) - 1
    else:
        # if there is not header
        line_num = sum(1 for _ in file.strip().split('\n'))
    if line_num < 2:
        raise ValueError
    return line_num


def examine_csv(
            file: str,
            csv_dialect: CsvDialectDTO = None
        ) -> Tuple[Type[csv.Dialect], bool]:
    """ Return csv dialect and True if dataset has a header """
    sniffer = csv.Sniffer()
    dialect = sniffer.sniff(file)
    has_header = sniffer.has_header(file)
    if csv_dialect:
        dialect.delimiter = csv_dialect.delimiter.value
        dialect.quotechar = csv_dialect.quotechar.value
        has_header = csv_dialect.has_header
    return dialect, has_header


def handle_duplicate_fieldnames(fieldnames: Sequence[str]) -> Optional[List]:
    """ compare list of fieldnames with set of unique field names length and
        return keys for fields in case the first one is longer
    """
    if len(fieldnames) > len(set(fieldnames)):
        keys = list(i for i in range(len(fieldnames)))
        return keys
    return None


def read_csv(
            filename: str,
            filepath: str,
            csv_dialect: CsvDialectDTO = None
        ) -> DatasetInfoDTO:
    """ Count lines, fields and read several lines
        from the file to determine datatypes
    """
    try:
        with open(filepath, 'r') as file:
            data = file.read()
    except FileNotFoundError:
        raise FileAccessError("Cannot find the dataset file")
    except PermissionError:
        raise FileAccessError("Dataset file reading is not permitted.")
    except OSError:
        raise FileAccessError("Cannot read dataset file")
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
    rows_to_read = settings.SAMPLE_ROWS_COUNT
    if line_num < rows_to_read:
        rows_to_read = line_num
    datarows = [next(reader) for _ in range(1, rows_to_read)]
    start_row = settings.CSV_STARTING_ROW
    if csv_dialect.start_row:
        start_row = csv_dialect.start_row
    column_types = [check_type(str(v)) for v in datarows[start_row].values()]
    file_info = DatasetInfoDTO(
        name=filename,
        height=line_num,
        width=sum(1 for _ in fieldnames),
        column_names=reader.fieldnames,
        column_types=column_types,
        datarows=datarows,
        csv_dialect=csv_dialect
    )
    return file_info


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
    if str_value.lower() == "true" or str_value.lower() == "false":
        return ColumnType.BOOLEAN
    return ColumnType.STRING
