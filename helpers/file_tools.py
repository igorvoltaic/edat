""" Collection of helper function for working with files and directories """
import glob
import os
import shutil
import uuid
from tempfile import gettempdir
from typing import Optional

from django.conf import settings


def mediadir():
    """ Return media/ full path """
    return os.path.join(settings.MEDIA_ROOT, 'media/')


def tmpdir():
    """ Return tmpdir full path """
    return os.path.join(gettempdir(), settings.PROJECT_NAME)


def create_temporary_file(
        filename: str,
        file_id: str,
        content: bytes) -> str:
    """ Create a temporary file and write uploaded data inside it """
    dirpath = os.path.join(tmpdir(), file_id)
    os.mkdir(dirpath)
    filepath = os.path.join(dirpath, filename)
    with open(filepath, 'wb') as file:
        file.write(content)
    return filepath


def create_tmpdir():
    """ create tmpdir and return its full path """
    temp_dir = tmpdir()
    if not os.path.isdir(temp_dir):
        os.mkdir(temp_dir)
    return temp_dir


def get_dir_path(file_path: str) -> str:
    """ return directory path """
    dir_path = os.path.split(file_path)[0]
    return dir_path


def get_file_id() -> str:
    """ Return new uuid for a file as a string """
    return str(uuid.uuid4())


def get_tmpfile_dirpath(file_id: str) -> Optional[str]:
    """ Return file directory path based on file's id """
    tmp_file_dir = os.path.join(tmpdir(), file_id)
    try:
        glob.glob(f"{tmp_file_dir}/*.csv")[0]
        return tmp_file_dir
    except IndexError:
        return None


def get_tmpfile_name(file_id: str) -> Optional[str]:
    """ Return file path based on file's id """
    tmp_file_dir = os.path.join(tmpdir(), file_id)
    try:
        filepath = glob.glob(f"{tmp_file_dir}/*.csv")[0]
        filename = os.path.split(filepath)[1]
        return filename
    except IndexError:
        return None


def get_tmpfile_path(file_id: str) -> Optional[str]:
    """ Return file path based on file's id """
    tmp_file_dir = os.path.join(tmpdir(), file_id)
    try:
        tempfile = glob.glob(f"{tmp_file_dir}/*.csv")[0]
        return tempfile
    except IndexError:
        return None


def move_tmpfile_to_media(file_id: str) -> Optional[str]:
    """ Move file and return full file path """
    tmpdirpath = os.path.join(tmpdir(), file_id)
    dst = mediadir()
    try:
        media_file_dir = shutil.move(tmpdirpath, dst)
    except OSError:
        return None
    media_file_path = glob.glob(f"{media_file_dir}/*.csv")[0]
    return media_file_path
