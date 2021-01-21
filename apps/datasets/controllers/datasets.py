""" Dataset app controller layer
"""
from fastapi import APIRouter, HTTPException, File, UploadFile, Request, \
        Response
from fastapi.responses import JSONResponse
from celery.exceptions import NotRegistered

from apps.datasets.services import get_all_datasets, read_dataset, \
    handle_uploaded_file, delete_tmpfile, edit_dataset_entry, \
    create_dataset_entry, delete_dataset_entry, get_plot_img, \
    read_temporary_file, get_render_status

from apps.datasets.dtos import CreateDatasetDTO, DatasetDTO, PageDTO, \
        DatasetInfoDTO, CsvDialectDTO, PlotDTO, PlotTaskStatusDTO

from helpers.auth_tools import login_required
from helpers.exceptions import FileAccessError, PlotRenderError


api_router = APIRouter()


# DATASET CONTROLLERS

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
    try:
        dataset = read_dataset(dataset_id)
    except FileAccessError as err:
        raise HTTPException(
            status_code=404,
            detail=err.message
        ) from err
    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset not found")
    return dataset


@api_router.post("/dataset", response_model=DatasetDTO, status_code=201)
@login_required
def create_dataset(request: Request, file_info: CreateDatasetDTO):
    """ Create new dataset DB entry and return dataset info """
    try:
        dataset = create_dataset_entry(file_info)  # type: ignore
    except FileAccessError as err:
        raise HTTPException(
            status_code=422,
            detail=err.message
        ) from err
    if not dataset:
        raise HTTPException(status_code=422, detail="Dataset creation error")
    return dataset


@api_router.post("/dataset/{dataset_id}", response_model=DatasetDTO)
@login_required
def reread_dataset(request: Request, dataset_id: int, dialect: CsvDialectDTO):
    """ Re-read dataset file using new user-supplied csv dialect """
    try:
        dataset = read_dataset(dataset_id, dialect)
    except FileAccessError as err:
        raise HTTPException(
            status_code=404,
            detail=err.message
        ) from err
    if not dataset:
        raise HTTPException(status_code=422, detail="Dataset amendment error")
    return dataset


@api_router.put("/dataset/{dataset_id}", response_model=DatasetDTO)
@login_required
def edit_dataset(request: Request, dataset_id: int, body: DatasetDTO):
    """ Edit dataset column types and comment """
    dataset = edit_dataset_entry(dataset_id, body)  # type: ignore
    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset not found")
    return dataset


@api_router.delete("/dataset/{dataset_id}", response_model=DatasetInfoDTO)
@login_required
def delete_dataset(request: Request, dataset_id: int):
    """ Call delete service and return deleted dataset info """
    dataset = delete_dataset_entry(dataset_id)  # type: ignore
    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset not found")
    return dataset


# TEMP FILE CONTROLLERS

@api_router.get("/upload/{file_id}", response_model=CreateDatasetDTO)
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


@api_router.post("/upload", response_model=CreateDatasetDTO)
@login_required
def upload_dataset_file(
            request: Request,
            response: Response,
            file: UploadFile = File(...)
        ):
    """ Receive CSV file and return temporary file id """
    if file.filename.split('.')[-1].lower() != "csv" \
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


@api_router.post("/upload/{file_id}", response_model=CreateDatasetDTO)
@login_required
def reread_tmpfile(request: Request, file_id: str, dialect: CsvDialectDTO):
    """ Re-read dataset temporary file using new user-supplied csv dialect """
    try:
        dataset = read_temporary_file(file_id=file_id, dialect=dialect)
    except FileAccessError as err:
        raise HTTPException(
                    status_code=503,
                    detail=err.message
        ) from err
    if not dataset:
        raise HTTPException(status_code=422, detail="Dataset amendment error")
    return dataset


@api_router.delete("/upload/{file_id}", status_code=200)
@login_required
def delete_temparary_file(request: Request, file_id: str):
    """ Remove temporary dataset file and confirmation message """
    deleted_file_id = delete_tmpfile(file_id)
    if not deleted_file_id:
        raise HTTPException(status_code=404, detail="File not found")
    return JSONResponse(content={"message": "submission cancelled"})


# PLOT CONTROLERS

@api_router.post("/render")
@login_required
def draw_dataset_plot(
            request: Request,
            response: Response,
            body: PlotDTO
        ):
    """ Return location of dataset image """
    try:
        plot = get_plot_img(body)  # type: ignore
    except FileAccessError as err:
        raise HTTPException(status_code=404, detail=err.message) from err
    if not plot:
        raise HTTPException(status_code=404, detail="Dataset not found")
    if plot.created:
        response.headers["Content-Location"] = f"/api/render/{plot.task_id}"
        response.status_code = 202
    else:
        response.headers["Content-Location"] = f"/{plot.path}"
        response.status_code = 303
    return response


@api_router.get("/render/{task_id}", response_model=PlotTaskStatusDTO)
@login_required
def check_render_status(
            request: Request,
            task_id: str
        ):
    """ Return status of dataset plot rendering process """
    try:
        render_status = get_render_status(task_id)
    except FileAccessError as err:
        raise HTTPException(status_code=404, detail=err.message) from err
    except PlotRenderError as err:
        raise HTTPException(status_code=400, detail=err.message) from err
    return render_status
