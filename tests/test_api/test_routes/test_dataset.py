import json
import pytest
import uuid
from fastapi import FastAPI
from httpx import AsyncClient
from starlette.status import HTTP_200_OK, HTTP_307_TEMPORARY_REDIRECT, \
        HTTP_404_NOT_FOUND

from apps.datasets.dtos import CreateDatasetDTO, CsvDialectDTO

pytestmark = pytest.mark.asyncio


@pytest.fixture
def csv_dialect() -> CsvDialectDTO:
    return CsvDialectDTO(
        delimiter=';',
        quotechar='"',
        has_header=True,
        start_row=0
    )


@pytest.fixture
def dataset(csv_dialect: CsvDialectDTO) -> CreateDatasetDTO:
    return CreateDatasetDTO(
        file_id=str(uuid.uuid4()),
        name="testing.csv",
        comment="test description",
        width=3,
        height=10,
        column_names=("test", "testing", "pytest"),
        column_types=("number", "float", "string"),
        csv_dialect=csv_dialect
    )


@pytest.mark.django_db
async def test_unauthorized_user_cannot_get_api_route(
    app: FastAPI, client: AsyncClient) -> None:
    response = await client.get("/api/dataset?page=1")
    response_url = str(response.url).split('/')[-1]
    assert response.history[0].status_code == HTTP_307_TEMPORARY_REDIRECT
    assert response_url == 'login'
    assert response.status_code == HTTP_200_OK


@pytest.mark.django_db
async def test_user_cannot_get_non_existent_dataset(
        app: FastAPI, authorized_client: AsyncClient) -> None:
    response = await authorized_client.get("/api/dataset/1")
    data = json.loads(response.text)
    assert len(response.history) == 0
    assert response.status_code == HTTP_404_NOT_FOUND
    assert data['detail'] == 'Dataset not found'


@pytest.mark.django_db
async def test_user_cannot_create_dataset_without_uploading_csv_file(
            app: FastAPI,
            authorized_client: AsyncClient,
            dataset: CreateDatasetDTO
        ) -> None:
    response = await authorized_client.post(
            "/api/dataset",
            headers={"Content-Type": "application/json"},
            json=dataset.dict(),
        )
    data = json.loads(response.text)
    assert response.status_code != HTTP_200_OK
    assert data['detail'] == "Cannot find temporary file"
