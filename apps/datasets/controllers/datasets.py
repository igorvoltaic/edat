""" Dataset app controller layer
"""
from fastapi import APIRouter, HTTPException, File, UploadFile
from fastapi.responses import JSONResponse

from apps.datasets.services import get_all_datasets, get_dataset, \
    handle_uploaded_file, get_dataset_info, \
    save_dataset, delete_dataset, \
    delete_tmpfile
from apps.datasets.dtos import DatasetDTO, PageDTO, FileDTO

api_router = APIRouter()


@api_router.get("/datasets", response_model=PageDTO)
def read_all(page: int, query: str = None):
    """ Return a page with dataset list """
    page_data = get_all_datasets(page, query)
    return page_data


@api_router.get("/datasets/{dataset_id}", response_model=DatasetDTO)
def read(dataset_id: int):
    """ Open dataset and visualize data """
    dataset = get_dataset(dataset_id)
    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset not found")
    return dataset


@api_router.get("/edit/{dataset_id}", response_model=FileDTO)
def edit_dataset_info(dataset_id: int):
    """ Edit dataset column types and comment """
    file_info = get_dataset_info(dataset_id)
    if not file_info:
        raise HTTPException(status_code=404, detail="Dataset not found")
    return file_info


@api_router.post("/datasets", response_model=FileDTO)
def upload_dataset_file(file: UploadFile = File(...)):
    """ Receive CSV file and """
    if file.filename.split('.')[-1] != "csv" \
            or file.content_type != "text/csv":
        raise HTTPException(status_code=422, detail="Unprocessable file type")
    file_info = handle_uploaded_file(file.filename, file.file.read())
    return file_info


@api_router.post("/save", response_model=DatasetDTO)
def save(file_info: FileDTO):
    """ Create new dataset DB entry and return dataset info """
    dataset = save_dataset(file_info)
    if not dataset:
        raise HTTPException(status_code=422,
                            detail="Was not able to save file")
    return dataset


@api_router.delete("/datasets/{dataset_id}", response_model=DatasetDTO)
def delete_item(dataset_id: int):
    """ Call delete service and return deleted dataset info """
    dataset = delete_dataset(dataset_id)
    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset not found")
    return dataset


@api_router.delete("/editor/{file_id}", status_code=204)
def delete_dataset_file(file_id: str):
    """ Remove temporary dataset file and return file id """
    deleted_file_id = delete_tmpfile(file_id)
    if not deleted_file_id:
        raise HTTPException(status_code=404, detail="File not found")
    return JSONResponse(content={"message": "submission cancelled"})
