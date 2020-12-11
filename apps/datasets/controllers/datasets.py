""" Dataset app controller layer
"""
from fastapi import APIRouter, HTTPException, File, UploadFile, Request
from fastapi.responses import JSONResponse

from apps.datasets.services import get_all_datasets, read_dataset, \
    handle_uploaded_file, delete_tmpfile, edit_dataset, \
    create_dataset, delete_dataset

from apps.datasets.dtos import CreateDatasetDTO, DatasetDTO, PageDTO, \
        DatasetInfoDTO, CsvDialectDTO

from helpers.auth_tools import login_required


api_router = APIRouter()


@api_router.get("/datasets", response_model=PageDTO)
@login_required
def read_all(request: Request, page: int, query: str = None):
    """ Return a page with dataset list """
    page_data = get_all_datasets(page, query)
    return page_data


@api_router.get("/datasets/{dataset_id}", response_model=DatasetDTO)
@login_required
def get_dataset(request: Request, dataset_id: int):
    """ Open dataset and visualize data """
    dataset = read_dataset(dataset_id)
    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset not found")
    return dataset


@api_router.put("/datasets/{dataset_id}", response_model=DatasetDTO)
@login_required
def edit_dataset_info(request: Request, dataset_id: int, body: DatasetDTO):
    """ Edit dataset column types and comment """
    dataset = edit_dataset(dataset_id, body)  # type: ignore
    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset not found")
    return dataset


@api_router.post("/datasets", response_model=CreateDatasetDTO)
@login_required
def upload_dataset_file(request: Request, file: UploadFile = File(...)):
    """ Receive CSV file and """
    if file.filename.split('.')[-1] != "csv" \
            or file.content_type != "text/csv":
        raise HTTPException(status_code=422, detail="Unprocessable file type")
    file_info = handle_uploaded_file(file.filename, file.file.read())
    return file_info


@api_router.post("/reread/{dataset_id}", response_model=DatasetDTO)
@login_required
def reread_dataset(request: Request, dataset_id: int, body: CsvDialectDTO):
    """ Create new dataset DB entry and return dataset info """
    dataset = read_dataset(dataset_id, body)  # type: ignore
    if not dataset:
        raise HTTPException(status_code=422, detail="Dataset amendment error")
    return dataset


@api_router.post("/reread", response_model=CreateDatasetDTO)
@login_required
def reread_tmpfile(request: Request, file_id: str, dialect: CsvDialectDTO):
    """ Create new dataset DB entry and return dataset info """
    dataset = handle_uploaded_file(file_id=file_id, dialect=dialect)
    if not dataset:
        raise HTTPException(status_code=422, detail="Dataset amendment error")
    return dataset


@api_router.post("/create", response_model=DatasetDTO)
@login_required
def create(request: Request, file_info: CreateDatasetDTO):
    """ Create new dataset DB entry and return dataset info """
    dataset = create_dataset(file_info)  # type: ignore
    if not dataset:
        raise HTTPException(status_code=422, detail="Dataset creation error")
    return dataset


@api_router.delete("/datasets/{dataset_id}", response_model=DatasetInfoDTO)
@login_required
def delete(request: Request, dataset_id: int):
    """ Call delete service and return deleted dataset info """
    dataset = delete_dataset(dataset_id)  # type: ignore
    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset not found")
    return dataset


@api_router.delete("/create/{file_id}", status_code=204)
@login_required
def delete_temparary_file(request: Request, file_id: str):
    """ Remove temporary dataset file and return file id """
    deleted_file_id = delete_tmpfile(file_id)
    if not deleted_file_id:
        raise HTTPException(status_code=404, detail="File not found")
    return JSONResponse(content={"message": "submission cancelled"})
