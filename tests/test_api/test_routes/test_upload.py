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

pytestmark = pytest.mark.asyncio


@pytest.fixture
def test_file() -> bytes:
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
    return data.encode()


"""
@pytest.mark.django_db
async def test_user_create_upload(
            app: FastAPI,
            authorized_client: AsyncClient,
            test_file: bytes
        ) -> None:
    response = await authorized_client.post(
            "/api/dataset",
            headers={"Content-Type": "application/json"},
            json=create_upload.dict(),
        )
    data = json.loads(response.text)
    assert response.status_code == HTTP_201_CREATED
    assert data['id'] == 1


@pytest.mark.django_db
async def test_user_get_upload(
        app: FastAPI, authorized_client: AsyncClient) -> None:
    response = await authorized_client.get("/api/dataset/1")
    data = json.loads(response.text)
    assert len(response.history) == 0
    assert response.status_code == HTTP_200_OK
    assert data['name'] == 'test_file.csv'


@pytest.mark.django_db
async def test_user_reread_upload(
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
async def test_user_edit_upload(
            app: FastAPI,
            authorized_client: AsyncClient,
        ) -> None:
    get_upload = await authorized_client.get("/api/dataset/1")
    dataset = json.loads(get_upload.text)
    response = await authorized_client.put(
            "/api/dataset/1",
            headers={"Content-Type": "application/json"},
            json=dataset,
        )
    data = json.loads(response.text)
    assert response.status_code == HTTP_200_OK
    assert data['id'] == 1


@pytest.mark.django_db
async def test_user_delete_upload(
        app: FastAPI, authorized_client: AsyncClient) -> None:
    response = await authorized_client.delete("/api/dataset/1")
    data = json.loads(response.text)
    assert len(response.history) == 0
    assert response.status_code == HTTP_200_OK
    assert data['name'] == 'test_file.csv'
"""
