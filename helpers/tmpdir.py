import os
from django.conf import settings


def tmpdir():
    return os.path.join(settings.MEDIA_ROOT, 'tmpdir/')
