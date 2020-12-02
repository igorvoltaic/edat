""" Helper to return temporary directory path """
import os
from tempfile import gettempdir
from django.conf import settings


def tmpdir():
    """ Return tmpdir full path """
    return os.path.join(gettempdir(), settings.PROJECT_NAME)
