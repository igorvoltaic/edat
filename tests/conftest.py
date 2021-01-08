import pytest
import uuid
from typing import Iterator

from asgi_lifespan import LifespanManager
from asgiref.sync import sync_to_async
from django.contrib.sessions.backends.db import SessionStore
from fastapi import FastAPI
from httpx import AsyncClient


@pytest.fixture
def app() -> FastAPI:
    from base.asgi import get_application  # local import for testing purpose
    return get_application()


@pytest.fixture
async def initialized_app(app: FastAPI) -> Iterator[FastAPI]:
    async with LifespanManager(app):
        yield app


@pytest.fixture
def test_password() -> str:
    return 'strong-test-pass'


@pytest.fixture
def create_user(db, django_user_model, test_password):
    def make_user(**kwargs):
        kwargs['password'] = test_password
        if 'username' not in kwargs:
            kwargs['username'] = str(uuid.uuid4())
        return django_user_model.objects.create_user(**kwargs)
    return make_user


@pytest.fixture
async def client(app: FastAPI) -> Iterator[AsyncClient]:
    async with AsyncClient(
            app=app,
            headers={"Content-Type": "application/json"},
            base_url="http://localhost"
    ) as client:
        print("Client is ready")
        yield client


@pytest.fixture
@sync_to_async
def session_id(create_user) -> str:
    user = create_user()
    s = SessionStore()
    s.create()
    s['user_id'] = user.id
    return s.session_key


@pytest.fixture
async def authorized_client(client: AsyncClient, session_id) -> AsyncClient:
    session = await session_id
    client.cookies.set(name='sessionid', value=session)
    yield client
