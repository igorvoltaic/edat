""" Check if the file is new
"""
from .get_tmpfilepath import get_tmpfilepath


def is_new_file(file_id: str) -> bool:
    """ Return True if it is a temp file, else return False """
    try:
        get_tmpfilepath(file_id)
    except IndexError:
        return False
    return True
