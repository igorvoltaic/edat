import os
import pytest
import shutil
import uuid
from asgiref.sync import sync_to_async
from httpx import AsyncClient
from starlette.status import HTTP_200_OK, HTTP_307_TEMPORARY_REDIRECT, \
        HTTP_404_NOT_FOUND, HTTP_201_CREATED

from apps.datasets.models import Dataset, Column, CsvDialect
from apps.datasets.dtos import CreateDatasetDTO, CsvDialectDTO, DatasetDTO, \
        ColumnType, Delimiter, Quotechar
from apps.datasets.services import delete_dataset_entry
from helpers.file_tools import tmpdir

pytestmark = pytest.mark.asyncio


@sync_to_async
def delete_dataset(id):
    return delete_dataset_entry(id)


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


@pytest.fixture
def clean_media():
    shutil.rmtree('./../tests/media')
    os.mkdir('./../tests/media')


@pytest.fixture
@sync_to_async
def test_dataset(
            test_file: str,
            create_dataset: CreateDatasetDTO
            ) -> DatasetDTO:
    dataset = Dataset.objects.create(  # type: ignore
            name=create_dataset.name,
            height=create_dataset.height,
            width=create_dataset.width,
            comment=create_dataset.comment
    )
    for index, data in enumerate(zip(  # type: ignore
        create_dataset.column_names,
        create_dataset.column_types)
    ):
        Column.objects.create(  # type: ignore
                dataset=dataset,
                index=index,
                name=data[0],
                datatype=ColumnType(data[1]),
            )
    csv_dialect = CsvDialect.objects.create(  # type: ignore
        dataset_id=dataset.id,
        delimiter=Delimiter(create_dataset.csv_dialect.delimiter),
        quotechar=Quotechar(create_dataset.csv_dialect.quotechar),
        has_header=create_dataset.csv_dialect.has_header,
        start_row=create_dataset.csv_dialect.start_row
    )
    dataset.file = test_file
    dataset.save()
    csv_dialect.save()
    return DatasetDTO(
            id=dataset.id,
            name=dataset.name,
            timestamp=dataset.timestamp,
            width=dataset.width,
            height=dataset.height,
            comment=dataset.comment,
            column_names=create_dataset.column_names,
            column_types=create_dataset.column_types,
    )


@pytest.mark.django_db
@pytest.mark.usefixtures("app")
class TestUnauthorizedClient:
    async def test_client_cannot_get_api_route(
            self, client: AsyncClient) -> None:
        response = await client.get("/api/dataset?page=1")
        response_url = str(response.url).split('/')[-1]
        assert response.history[0].status_code == HTTP_307_TEMPORARY_REDIRECT
        assert response_url == 'login'
        assert response.status_code == HTTP_200_OK


@pytest.mark.django_db
@pytest.mark.usefixtures("app")
class TestAuthorizedClient:
    async def test_user_cannot_get_non_existent_dataset(
             self,
             authorized_client: AsyncClient) -> None:
        response = await authorized_client.get("/api/dataset/1")
        data = response.json()
        assert len(response.history) == 0
        assert response.status_code == HTTP_404_NOT_FOUND
        assert data['detail'] == 'Dataset not found'

    async def test_user_cannot_create_dataset_without_uploading_csv_file(
                self,
                authorized_client: AsyncClient,
                create_dataset: CreateDatasetDTO,
            ) -> None:
        create_dataset.file_id = str(uuid.uuid4())
        response = await authorized_client.post(
                "/api/dataset",
                headers={"Content-Type": "application/json"},
                json=create_dataset.dict(),
            )
        data = response.json()
        assert response.status_code != HTTP_200_OK
        assert data['detail'] == "Cannot find temporary file"

    @pytest.mark.usefixtures("clean_media", "test_file")
    async def test_user_create_dataset(
                self,
                authorized_client: AsyncClient,
                create_dataset: CreateDatasetDTO,
            ) -> None:
        response = await authorized_client.post(
                "/api/dataset",
                headers={"Content-Type": "application/json"},
                json=create_dataset.dict(),
            )
        data = response.json()
        delete_dataset(data['id'])
        assert 'id' in data.keys()
        assert response.status_code == HTTP_201_CREATED
        assert data['name'] == 'test_file.csv'

    async def test_user_get_dataset(
            self,
            authorized_client: AsyncClient,
            test_dataset) -> None:
        dataset = await test_dataset
        response = await authorized_client.get(f"/api/dataset/{dataset.id}")
        data = response.json()
        assert len(response.history) == 0
        assert response.status_code == HTTP_200_OK
        assert data['name'] == dataset.name
        assert data['id'] == dataset.id
        assert data['csv_dialect']['delimiter'] == ';'

    async def test_user_reread_dataset(
                self,
                authorized_client: AsyncClient,
                csv_dialect: CsvDialectDTO,
                test_dataset
            ) -> None:
        dataset = await test_dataset
        dialect = csv_dialect.dict()
        dialect['delimiter'] = ','
        test_dialect = dialect
        response = await authorized_client.post(
                f"/api/dataset/{dataset.id}",
                headers={"Content-Type": "application/json"},
                json=test_dialect,
            )
        data = response.json()
        assert response.status_code == HTTP_200_OK
        assert data['id'] == dataset.id
        assert data['csv_dialect']['delimiter'] == ','

    async def test_user_edit_dataset(
                self,
                authorized_client: AsyncClient,
                test_dataset
            ) -> None:
        dataset = await test_dataset
        dataset.comment = 'helloworld'
        dataset.timestamp = str(dataset.timestamp)
        response = await authorized_client.put(
                f"/api/dataset/{dataset.id}",
                headers={"Content-Type": "application/json"},
                json=dataset.dict(),
        )
        data = response.json()
        assert response.status_code == HTTP_200_OK
        assert data['id'] == dataset.id
        assert data['comment'] == 'helloworld'

    async def test_user_delete_dataset(
                self,
                authorized_client: AsyncClient,
                test_dataset
            ) -> None:
        dataset = await test_dataset
        response = await authorized_client.delete(f"/api/dataset/{dataset.id}")
        data = response.json()
        assert len(response.history) == 0
        assert response.status_code == HTTP_200_OK
        assert data['name'] == 'test_file.csv'
