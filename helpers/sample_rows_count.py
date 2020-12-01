""" helper which returns number of rows to read for data sample
"""


def sample_rows_count(line_num: int) -> int:
    """ Return number of rows """
    rows_count = 21
    if line_num < 21:
        rows_count = line_num - 1
    return rows_count
