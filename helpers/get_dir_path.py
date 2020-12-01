""" Helper which returns directory path to a file """
import os


def get_dir_path(file_path: str) -> str:
    """ return directory path """
    dir_path = os.path.split(file_path)[0]
    return dir_path
