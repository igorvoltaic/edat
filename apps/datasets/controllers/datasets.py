""" Dataset app controller layer
"""
from fastapi import APIRouter, HTTPException, File, UploadFile, Request, \
        Response
from fastapi.responses import JSONResponse

from apps.datasets.services import get_all_datasets, read_dataset, \
    handle_uploaded_file, delete_tmpfile, edit_dataset_entry, \
    create_dataset_entry, delete_dataset_entry, get_plot_img

from apps.datasets.dtos import CreateDatasetDTO, DatasetDTO, PageDTO, \
        DatasetInfoDTO, CsvDialectDTO, CreatePlotDTO, PlotDTO

from helpers.auth_tools import login_required
from helpers.exceptions import FileAccessError


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
def upload_dataset_file(request: Request, file: UploadFile = File(...)):
    """ Receive CSV file and """
    if file.filename.split('.')[-1] != "csv" \
            or file.content_type != "text/csv":
        raise HTTPException(status_code=422, detail="Unprocessable file type")
    try:
        file_info = handle_uploaded_file(file.filename, file.file.read())
    except FileAccessError as e:
        raise HTTPException(
                    status_code=503,
                    detail=e.message
        )
    return file_info


@api_router.post("/reread/{dataset_id}", response_model=DatasetDTO)
@login_required
def reread_dataset(request: Request, dataset_id: int, dialect: CsvDialectDTO):
    """ Re-read dataset file using new user-supplied csv dialect """
    dataset = read_dataset(dataset_id, dialect)  # type: ignore
    if not dataset:
        raise HTTPException(status_code=422, detail="Dataset amendment error")
    return dataset


@api_router.post("/reread", response_model=CreateDatasetDTO)
@login_required
def reread_tmpfile(request: Request, file_id: str, dialect: CsvDialectDTO):
    """ Re-read dataset temporary file using new user-supplied csv dialect """
    try:
        dataset = handle_uploaded_file(file_id=file_id, dialect=dialect)
    except FileAccessError as e:
        raise HTTPException(
                    status_code=503,
                    detail=e.message
        )
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


@api_router.delete("/create/{file_id}", status_code=204)
@login_required
def delete_temparary_file(request: Request, file_id: str):
    """ Remove temporary dataset file and return file id """
    deleted_file_id = delete_tmpfile(file_id)
    if not deleted_file_id:
        raise HTTPException(status_code=404, detail="File not found")
    return JSONResponse(content={"message": "submission cancelled"})


@api_router.post("/render", status_code=204)
@login_required
def draw_dataset_plot(
            request: Request,
            response: Response,
            body: CreatePlotDTO
        ):
    """ Return a page with dataset list """
    try:
        plot_img_path = get_plot_img(
                body.id,
                body.height,
                body.width,
                body.plot_type,
                body.params,
                body.columns,
        )
    except FileAccessError as e:
        raise HTTPException(
                    status_code=503,
                    detail=e.message
        )
    if not plot_img_path:
        raise HTTPException(status_code=422, detail="Plot creation error")
    response.headers["Content-Location"] = plot_img_path
    return response
