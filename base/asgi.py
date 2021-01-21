"""
ASGI config for base project.
It exposes the ASGI callable as a module-level variable named 'application'.
"""
from django.apps import apps
from django.conf import settings
from django.core.wsgi import get_wsgi_application
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.wsgi import WSGIMiddleware
from starlette.middleware.cors import CORSMiddleware

load_dotenv()
apps.populate(settings.INSTALLED_APPS)

# these two imports are only available once apps are populated
from apps.datasets.controllers.datasets import api_router  # noqa: E402
from helpers.file_tools import create_tmpdir, create_mediadir  # noqa: E402


def get_application() -> FastAPI:
    app = FastAPI(
        title=settings.PROJECT_NAME,
        debug=settings.DEBUG,
        docs_url=None,
        redoc_url=None,
        openapi_url=None
    )
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.ALLOWED_HOSTS or ["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.include_router(api_router, prefix="/api")
    app.mount("/", WSGIMiddleware(get_wsgi_application()))

    return app


# create paths needed for app operation
create_tmpdir()
create_mediadir()

app = get_application()
