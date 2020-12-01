""" Helper funciton to fetch in about dataset headers
"""
import csv
from csv import Dialect
from typing import Tuple, Type


def examine_csv(file: str) -> Tuple[Type[Dialect], bool]:
    """ Return dialect and True if dataset has a header """
    sniffer = csv.Sniffer()
    dialect = sniffer.sniff(file)
    has_header = sniffer.has_header(file)
    return dialect, has_header
