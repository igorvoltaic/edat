""" Helper funciton to get line count of csv file
"""


def count_lines(file: str, has_header: bool) -> int:
    """ Return number of lines in file """
    if has_header:
        # remove header line
        line_num = sum(1 for _ in file.strip().split('\n')) - 1
    else:
        # if there is not header
        line_num = sum(1 for _ in file.strip().split('\n'))
    return line_num
