""" Helper to get full temporary file path """
import os
import glob
from .tmpdir import tmpdir


def get_tmpfilepath(file_id: str) -> str:
    """ Return file path based in it's id """
    tmp_file_dir = os.path.join(tmpdir(), file_id)
    tmp_file_path = glob.glob(f"{tmp_file_dir}/*.csv")[0]
    return tmp_file_path
