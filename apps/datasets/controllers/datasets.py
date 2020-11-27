from fastapi import APIRouter, HTTPException, File, UploadFile

from apps.datasets.services import get_all_datasets, get_dataset, \
                                   read_csv, handle_uploaded_file, \
                                   save_dataset, delete_dataset
from apps.datasets.dtos import DatasetDTO, PageDTO, FileDTO

from helpers.recreate_filename import recreate_filename


api_router = APIRouter()


@api_router.get("/datasets", response_model=PageDTO)
def read_all(page: int, q: str = None):
    page_data = get_all_datasets(page, q)
    return page_data


@api_router.get("/datasets/{dataset_id}", response_model=DatasetDTO)
def read(dataset_id: int):
    dataset = get_dataset(dataset_id)
    file_info = read_csv(dataset.name, dataset.file_id, uploaded_file=True)
    dataset.file_info = file_info
    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset not found")
    return dataset


@api_router.post("/datasets", response_model=FileDTO)
def upload_dataset_file(file: UploadFile = File(...)):
    if file.filename.split('.')[-1] != "csv" \
            or file.content_type != "text/csv":
        raise HTTPException(status_code=422, detail="Unprocessable file type")
    file_info = handle_uploaded_file(file.filename, file.file.read())
    return file_info


@api_router.post("/save_dataset", response_model=DatasetDTO)
def save_dataset(file_info: FileDTO):
    dataset = save_dataset(tmpfile, column_names, column_types)
    pass


@api_router.delete("/datasets/{dataset_id}", response_model=DatasetDTO)
def delete_item(dataset_id: int):
    dataset = delete_dataset(dataset_id)
    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset not found")
    return dataset
