from tempfile import NamedTemporaryFile

from .tmpdir import tmpdir


def create_temporary_file(filename: str, content: bytes) -> str:
    """ Create a temporary file and write uploaded data inside it """
    prefix = (f"{filename}__tmpfile__")
    file = NamedTemporaryFile(
        prefix=prefix,
        delete=False,
        dir=tmpdir(),
        mode='wb'
    )
    file.write(content)
    file.close()
    return file.name
