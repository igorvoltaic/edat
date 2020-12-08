""" Helper for uploaded temp file creation """
import os

from .tmpdir import tmpdir


def create_temporary_file(filename: str, file_id: str, content: bytes) -> str:
    """ Create a temporary file and write uploaded data inside it """
    dirpath = os.path.join(tmpdir(), file_id)
    os.mkdir(dirpath)
    filepath = os.path.join(dirpath, filename)
    with open(filepath, 'wb') as file:
        file.write(content)
    return filepath
