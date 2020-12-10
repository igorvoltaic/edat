""" Helper funciton to get line count of csv file
"""
import csv
from typing import Tuple, Type
from django.conf import settings

from apps.datasets.dtos import CsvDialectDTO


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


def sample_rows_count(line_num: int) -> int:
    """ helper which returns number of rows to read for data sample """
    rows_count = settings.PREREAD_SAMPLE_ROWS
    if line_num < rows_count:
        # EXCLUDE top 2 rows: header + 1 row for datatype check_type(),
        # because we already read them
        rows_count = line_num - 2
    return rows_count
