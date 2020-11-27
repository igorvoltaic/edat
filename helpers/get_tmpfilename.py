import os


def get_tmpfilename(path: str) -> str:
    """ get path tail """
    return os.path.split(path)[1]
