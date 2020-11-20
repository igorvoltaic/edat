from typing import List
from fastapi import APIRouter, HTTPException, File, UploadFile

from apps.datasets.services import get_all_datasets, get_dataset, \
                                   read_csv, handle_uploaded_file, \
                                   save_dataset, delete_dataset
from apps.datasets.dtos import DatasetDTO


api_router = APIRouter()


@api_router.get("/datasets", response_model=List[DatasetDTO])
def read_all():
    datasets = get_all_datasets()
    return datasets


@api_router.get("/datasets/{dataset_id}", response_model=DatasetDTO)
def read(dataset_id: int):
    dataset = get_dataset(dataset_id)
    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset not found")
    return dataset


@api_router.post("/datasets")
# @api_router.post("/datasets", response_model=DatasetDTO)
def create_item(file: UploadFile = File(...)):
    if not file.filename.split('.')[-1] == "csv" \
            and not file.content_type == "text/csv":
        raise HTTPException(status_code=422, detail="Unprocessable file type")
    file_uuid = handle_uploaded_file(file.file)
    dataset_info = read_csv(file.filename, file_uuid)
    dataset = save_dataset(dataset_info)
    # return file_info
    return dataset


@api_router.delete("/datasets/{dataset_id}", response_model=List[DatasetDTO])
def delete_item(dataset_id: int):
    datasets = delete_dataset(dataset_id)
    if not datasets:
        raise HTTPException(status_code=404, detail="Dataset not found")
    return datasets
