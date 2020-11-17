"""
base URL Configuration
"""
from django.conf import settings
from django.contrib import admin
from django.contrib.staticfiles import views
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('apps.visualizer.urls')),
]

if settings.DEBUG:
    from django.urls import re_path

    urlpatterns += [re_path(r"^static/(?P<path>.*)$", views.serve)]
