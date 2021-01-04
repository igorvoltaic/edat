import pytest
from httpx import AsyncClient
from fastapi import FastAPI
from asgi_lifespan import LifespanManager
import httpx


@pytest.fixture
def app() -> FastAPI:
    from base.asgi import get_application  # local import for testing purpose
    return get_application()


@pytest.fixture
async def initialized_app(app: FastAPI) -> FastAPI:
    async with LifespanManager(app):
        yield app


@pytest.fixture
async def client(app):
    async with httpx.AsyncClient(app=app, base_url="http://localhost") as client:
        print("Client is ready")
        yield client

# @pytest.fixture
# async def client(app: FastAPI) -> AsyncClient:
#     async with LifespanManager(app):
#         async with AsyncClient(
#             app=app,
#             base_url="http://localhost",
#             headers={"Content-Type": "application/json"}
#         ) as client:
#             yield client
