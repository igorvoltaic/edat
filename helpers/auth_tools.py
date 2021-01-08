""" API login_required decorator """
import functools

from django.conf import settings
from django.contrib.sessions.models import Session
from starlette.responses import RedirectResponse


def login_required(func):
    """Make sure user is logged in before proceeding"""
    @functools.wraps(func)
    def wrapper_login_required(*args, **kwargs):
        request = kwargs['request']
        try:
            _ = Session.objects.get(pk=request.cookies.get('sessionid'))
        except Session.DoesNotExist:  # type: ignore
            response = RedirectResponse(url=settings.LOGIN_URL)
            return response
        return func(*args, **kwargs)
    return wrapper_login_required
