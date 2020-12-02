""" Helper used for creation of temporary directory path """
import os
from .tmpdir import tmpdir


def create_tmpdir():
    """ create  tmpdir full path """
    temp_dir = tmpdir()
    if not os.path.isdir(temp_dir):
        os.mkdir(temp_dir)
    return temp_dir
