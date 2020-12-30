"""
base URL Configuration
"""
from django.conf import settings
from django.contrib import admin
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.conf.urls.static import static
from django.urls import path, include

from helpers.file_tools import mediadir


handler404 = 'apps.visualizer.views.page_not_found'
handler500 = 'apps.visualizer.views.server_error'

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('apps.visualizer.urls')),
]

urlpatterns += static(settings.MEDIA_URL, document_root=mediadir())

if settings.DEBUG:
    urlpatterns += staticfiles_urlpatterns()
