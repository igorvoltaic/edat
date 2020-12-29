""" Dataset app controller layer
"""
from fastapi import APIRouter, HTTPException, File, UploadFile, Request, \
        Response
from fastapi.responses import JSONResponse

from apps.datasets.services import get_all_datasets, read_dataset, \
    handle_uploaded_file, delete_tmpfile, edit_dataset_entry, \
    create_dataset_entry, delete_dataset_entry, get_plot_img, \
    read_temporary_file

from apps.datasets.dtos import CreateDatasetDTO, DatasetDTO, PageDTO, \
        DatasetInfoDTO, CsvDialectDTO, PlotDTO

from helpers.auth_tools import login_required
from helpers.exceptions import FileAccessError, PlotRenderError


api_router = APIRouter()


@api_router.get("/dataset", response_model=PageDTO)
@login_required
def list_datasets(request: Request, page: int, query: str = None):
    """ Return a page with dataset list """
    page_data = get_all_datasets(page, query)
    return page_data


@api_router.get("/dataset/{dataset_id}", response_model=DatasetDTO)
@login_required
def get_dataset(request: Request, dataset_id: int):
    """ Open dataset and visualize data """
    dataset = read_dataset(dataset_id)
    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset not found")
    return dataset


@api_router.put("/dataset/{dataset_id}", response_model=DatasetDTO)
@login_required
def edit_dataset(request: Request, dataset_id: int, body: DatasetDTO):
    """ Edit dataset column types and comment """
    dataset = edit_dataset_entry(dataset_id, body)  # type: ignore
    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset not found")
    return dataset


@api_router.post("/dataset", response_model=CreateDatasetDTO)
@login_required
def upload_dataset_file(
            request: Request,
            response: Response,
            file: UploadFile = File(...)
        ):
    """ Receive CSV file and return temporary file id """
    if file.filename.split('.')[-1] != "csv" \
            or file.content_type != "text/csv":
        raise HTTPException(status_code=422, detail="Unprocessable file type")
    try:
        file_id = handle_uploaded_file(file.filename, file.file.read())
    except FileAccessError as err:
        raise HTTPException(
                    status_code=503,
                    detail=err.message
        ) from err
    response.headers["Location"] = file_id
    response.status_code = 204
    return response


@api_router.post("/read/{dataset_id}", response_model=DatasetDTO)
@login_required
def reread_dataset(request: Request, dataset_id: int, dialect: CsvDialectDTO):
    """ Re-read dataset file using new user-supplied csv dialect """
    dataset = read_dataset(dataset_id, dialect)  # type: ignore
    if not dataset:
        raise HTTPException(status_code=422, detail="Dataset amendment error")
    return dataset


@api_router.get("/read", response_model=CreateDatasetDTO)
@login_required
def read_tmpfile(request: Request, file_id: str):
    """ Read dataset temporary file in with supplied id """
    try:
        dataset = read_temporary_file(file_id=file_id)
    except FileAccessError as err:
        raise HTTPException(
                    status_code=503,
                    detail=err.message
        ) from err
    if not dataset:
        raise HTTPException(status_code=422, detail="Dataset reading error")
    return dataset


@api_router.post("/read", response_model=CreateDatasetDTO)
@login_required
def reread_tmpfile(request: Request, file_id: str, dialect: CsvDialectDTO):
    """ Re-read dataset temporary file using new user-supplied csv dialect """
    try:
        dataset = handle_uploaded_file(file_id=file_id, dialect=dialect)
    except FileAccessError as err:
        raise HTTPException(
                    status_code=503,
                    detail=err.message
        ) from err
    if not dataset:
        raise HTTPException(status_code=422, detail="Dataset amendment error")
    return dataset


@api_router.post("/create", response_model=DatasetDTO, status_code=201)
@login_required
def create_dataset(request: Request, file_info: CreateDatasetDTO):
    """ Create new dataset DB entry and return dataset info """
    dataset = create_dataset_entry(file_info)  # type: ignore
    if not dataset:
        raise HTTPException(status_code=422, detail="Dataset creation error")
    return dataset


@api_router.delete("/dataset/{dataset_id}", response_model=DatasetInfoDTO)
@login_required
def delete_dataset(request: Request, dataset_id: int):
    """ Call delete service and return deleted dataset info """
    dataset = delete_dataset_entry(dataset_id)  # type: ignore
    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset not found")
    return dataset


@api_router.delete("/create/{file_id}", status_code=200)
@login_required
def delete_temparary_file(request: Request, file_id: str):
    """ Remove temporary dataset file and return file id """
    deleted_file_id = delete_tmpfile(file_id)
    if not deleted_file_id:
        raise HTTPException(status_code=404, detail="File not found")
    return JSONResponse(content={"message": "submission cancelled"})


@api_router.post("/render")
@login_required
def draw_dataset_plot(
            request: Request,
            response: Response,
            body: PlotDTO
        ):
    """ Return location of dataset image """
    try:
        plot_img_path = get_plot_img(body)
    except FileAccessError as err:
        raise HTTPException(
            status_code=503,
            detail=err.message
        ) from err
    except PlotRenderError as err:
        raise HTTPException(
            status_code=400,
            detail=err.message
        ) from err
    if not plot_img_path:
        raise HTTPException(status_code=400, detail="Dataset not found")
    response.headers["Content-Location"] = f"/{plot_img_path}"
    response.status_code = 204
    return response
