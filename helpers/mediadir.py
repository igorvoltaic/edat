""" Helper to return media directory path """
import os
from django.conf import settings


def mediadir():
    """ Return media/ full path """
    return os.path.join(settings.MEDIA_ROOT, 'media/')
