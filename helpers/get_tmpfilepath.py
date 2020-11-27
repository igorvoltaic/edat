import os
from .tmpdir import tmpdir


def get_tmpfilepath(filename: str) -> str:
    """ get full temporary file path """
    tmp_file_path = os.path.join(tmpdir(), filename)
    return tmp_file_path
