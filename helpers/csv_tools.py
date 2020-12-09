""" Helper funciton to get line count of csv file
"""
import csv
from typing import Tuple, Type
from django.conf import settings


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


def examine_csv(file: str) -> Tuple[Type[csv.Dialect], bool]:
    """ Return csv dialect and True if dataset has a header """
    sniffer = csv.Sniffer()
    dialect = sniffer.sniff(file)
    has_header = sniffer.has_header(file)
    return dialect, has_header


def sample_rows_count(line_num: int) -> int:
    """ helper which returns number of rows to read for data sample """
    if line_num < settings.PREREAD_SAMPLE_ROWS:
        rows_count = line_num - 1
    return rows_count
