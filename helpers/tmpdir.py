""" Helper to return temporary directory path """
import os
from django.conf import settings


def tmpdir():
    """ Return tmpdir full path """
    return os.path.join(settings.MEDIA_ROOT, 'tmpdir/')
