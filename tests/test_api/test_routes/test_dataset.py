# import datetime
import json
import os
import pytest
import uuid
from fastapi import FastAPI
from httpx import AsyncClient
from starlette.status import HTTP_200_OK, HTTP_307_TEMPORARY_REDIRECT, \
        HTTP_404_NOT_FOUND, HTTP_201_CREATED

from apps.datasets.dtos import CreateDatasetDTO, CsvDialectDTO
from helpers.file_tools import tmpdir

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
def create_dataset(csv_dialect: CsvDialectDTO) -> CreateDatasetDTO:
    return CreateDatasetDTO(
        file_id='test_file_id',
        name="test_file.csv",
        comment="test description",
        width=3,
        height=10,
        column_names=("test", "testing", "pytest"),
        column_types=("number", "float", "string"),
        csv_dialect=csv_dialect
    )


@pytest.fixture
def test_file(create_dataset: CreateDatasetDTO) -> str:
    test_dir = os.path.join(tmpdir(), create_dataset.file_id)
    if not os.path.isdir(test_dir):
        os.mkdir(test_dir)
    test_file = os.path.join(test_dir, 'test_file.csv')
    data = str(
        '''
        year,month,passengers
        1949,January,112
        1949,February,118
        1949,March,132
        1949,April,129
        1949,May,121
        1949,June,135
        1949,July,148
        1949,August,148
        1949,September,136
        '''
    )
    with open(test_file, 'w') as csv:
        csv.write(data)
    return test_file


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
            create_dataset: CreateDatasetDTO,
        ) -> None:
    create_dataset.file_id = str(uuid.uuid4())
    response = await authorized_client.post(
            "/api/dataset",
            headers={"Content-Type": "application/json"},
            json=create_dataset.dict(),
        )
    data = json.loads(response.text)
    assert response.status_code != HTTP_200_OK
    assert data['detail'] == "Cannot find temporary file"


@pytest.mark.django_db
async def test_user_create_dataset(
            app: FastAPI,
            authorized_client: AsyncClient,
            create_dataset: CreateDatasetDTO,
            test_file: str
        ) -> None:
    response = await authorized_client.post(
            "/api/dataset",
            headers={"Content-Type": "application/json"},
            json=create_dataset.dict(),
        )
    data = json.loads(response.text)
    assert response.status_code == HTTP_201_CREATED
    assert data['id'] == 1


@pytest.mark.django_db
async def test_user_get_dataset(
        app: FastAPI, authorized_client: AsyncClient) -> None:
    response = await authorized_client.get("/api/dataset/1")
    data = json.loads(response.text)
    assert len(response.history) == 0
    assert response.status_code == HTTP_200_OK
    assert data['name'] == 'test_file.csv'


@pytest.mark.django_db
async def test_user_reread_dataset(
            app: FastAPI,
            authorized_client: AsyncClient,
            csv_dialect: CsvDialectDTO
        ) -> None:
    dialect = csv_dialect.dict()
    dialect['delimiter'] = ','
    response = await authorized_client.post(
            "/api/dataset/1",
            headers={"Content-Type": "application/json"},
            json=dialect,
        )
    data = json.loads(response.text)
    assert response.status_code == HTTP_200_OK
    assert data['id'] == 1
    assert data['csv_dialect']['delimiter'] == ','


@pytest.mark.django_db
async def test_user_edit_dataset(
            app: FastAPI,
            authorized_client: AsyncClient,
        ) -> None:
    get_dataset = await authorized_client.get("/api/dataset/1")
    dataset = json.loads(get_dataset.text)
    response = await authorized_client.put(
            "/api/dataset/1",
            headers={"Content-Type": "application/json"},
            json=dataset,
        )
    data = json.loads(response.text)
    assert response.status_code == HTTP_200_OK
    assert data['id'] == 1


@pytest.mark.django_db
async def test_user_delete_dataset(
        app: FastAPI, authorized_client: AsyncClient) -> None:
    response = await authorized_client.delete("/api/dataset/1")
    data = json.loads(response.text)
    assert len(response.history) == 0
    assert response.status_code == HTTP_200_OK
    assert data['name'] == 'test_file.csv'
