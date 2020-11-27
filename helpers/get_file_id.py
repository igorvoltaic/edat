import uuid


def get_file_id() -> str:
    """ Create a uniq temp file id """
    return str(uuid.uuid4())
