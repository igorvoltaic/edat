import pytest
import uuid
from fastapi import FastAPI
from httpx import AsyncClient
from starlette.status import HTTP_200_OK

from apps.datasets.dtos import CreateDatasetDTO, ColumnType

pytestmark = pytest.mark.asyncio


@pytest.fixture
def new_dataset():
    return CreateDatasetDTO(
        file_id=str(uuid.uuid4()),
        name="testing.csv",
        comment="test description",
        width=3,
        height=10,
        column_names=("test", "testing", "pytest"),
        column_types=("number", "float", "string")
    )


@pytest.mark.django_db
async def test_user_can_get_dataset_list(
    app: FastAPI, client: AsyncClient) -> None:
    response = await client.get("/api/dataset?page=1")
    assert response.status_code == HTTP_200_OK


@pytest.mark.django_db
async def test_user_can_get_dataset(
    app: FastAPI, client: AsyncClient) -> None:
    response = await client.get("/api/dataset/1")
    assert response.status_code == HTTP_200_OK


@pytest.mark.django_db
async def test_user_can_create_dataset(
            app: FastAPI,
            client: AsyncClient,
            new_dataset: CreateDatasetDTO
        ) -> None:
    response = await client.post(
            "/api/dataset",
            headers={"Content-Type": "application/json"},
            json=new_dataset.json(),
        )
    # assert response.status_code == HTTP_200_OK
    assert response.text == "created"
