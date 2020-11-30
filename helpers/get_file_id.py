""" Helper to create uniq uiid for a tempfile
"""
import uuid


def get_file_id() -> str:
    """ Return new uuid as a string """
    return str(uuid.uuid4())
