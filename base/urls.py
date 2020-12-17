"""
base URL Configuration
"""
from django.conf import settings
from django.contrib import admin
from django.contrib.staticfiles import views
from django.conf.urls.static import static
from django.urls import path, include

from helpers.file_tools import mediadir

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('apps.visualizer.urls')),
] + static(settings.MEDIA_URL, document_root=mediadir())

if settings.DEBUG:
    from django.urls import re_path

    urlpatterns += [re_path(r"^static/(?P<path>.*)$", views.serve)]
