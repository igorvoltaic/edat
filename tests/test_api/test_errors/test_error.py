import pytest
from fastapi import FastAPI
from httpx import AsyncClient
from starlette.status import HTTP_404_NOT_FOUND, HTTP_200_OK

pytestmark = pytest.mark.asyncio


async def test_route_not_found_error(app: FastAPI):
    client = AsyncClient(base_url="http://localhost", app=app)
    response = await client.get("/wrong_path/asd")
    assert response.status_code == HTTP_404_NOT_FOUND


@pytest.mark.django_db
async def test_user_cannot_get_dataset_list_page(
    app: FastAPI, client: AsyncClient) -> None:
    response = await client.get("/api/dataset")
    assert response.status_code != HTTP_200_OK
