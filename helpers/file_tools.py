""" Collection of helper function for working with files and directories """
import glob
import os
import shutil
import uuid
from tempfile import gettempdir
from typing import Optional

from django.conf import settings
from helpers.exceptions import FileAccessError


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


def create_mediadir():
    """ create tmpdir and return its full path """
    media_dir = mediadir()
    if not os.path.isdir(media_dir):
        os.mkdir(media_dir)
    return media_dir


def create_tmpdir():
    """ create tmpdir and return its full path """
    temp_dir = tmpdir()
    if not os.path.isdir(temp_dir):
        os.mkdir(temp_dir)
    return temp_dir


def get_dir_path(file_path: str) -> str:
    """ return directory path """
    return os.path.split(file_path)[0]


def get_file_id() -> str:
    """ Return new uuid for a file as a string """
    return str(uuid.uuid4())


def get_tmpfile_dirpath(file_id: str) -> str:
    """ Return file directory path based on file's id """
    return os.path.join(tmpdir(), file_id)


def get_tmpfile_path(file_id: str) -> Optional[str]:
    """ Return file path based on file's id """
    tmp_file_dir = os.path.join(tmpdir(), file_id)
    try:
        tempfile = glob.glob(f"{tmp_file_dir}/*.csv")[0]
        return tempfile
    except IndexError:
        return None


def move_tmpfile_to_media(file_id: str, dataset_id: int) -> Optional[str]:
    """ Move file and return full file path """
    src = get_tmpfile_path(file_id)
    if not src:
        raise FileAccessError("Cannot find temporary file")
    filename = os.path.split(src)[1]
    dst_dir = os.path.join(mediadir(), str(dataset_id))
    try:
        os.mkdir(dst_dir)
    except FileExistsError:
        raise FileAccessError("Cannot save dataset file")
    dst = os.path.join(dst_dir, filename)
    try:
        dst = shutil.move(src, dst)
    # For permission related errors
    except FileNotFoundError:
        raise FileAccessError("Cannot move temporary file")
    except PermissionError:
        raise FileAccessError("Temporary file moving is not permitted.")
    except OSError:
        raise FileAccessError("Cannot move temporary file")
    return dst


def get_plot_img_name(csv_file: str, plot_id: int) -> str:
    """ Return filename for a new plot image """
    dataset_dir = get_dir_path(csv_file)
    image_dir = os.path.join(dataset_dir, 'images')
    if not os.path.isdir(image_dir):
        os.mkdir(image_dir)
    image_name = "plot_{}.png".format(plot_id)
    return os.path.join(image_dir, image_name)
