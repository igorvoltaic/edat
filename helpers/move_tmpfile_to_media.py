""" Helper to move selected file to media directory """
import os
import shutil
import glob
from .mediadir import mediadir
from .tmpdir import tmpdir


def move_tmpfile_to_media(file_id: str) -> str:
    """ Move file and return full file path """
    tmpdirpath = os.path.join(tmpdir(), file_id)
    dst = mediadir()
    media_file_dir = shutil.move(tmpdirpath, dst)
    media_file_path = glob.glob(f"{media_file_dir}/*.csv")[0]
    return media_file_path
