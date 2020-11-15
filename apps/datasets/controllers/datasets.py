from typing import List
from fastapi import APIRouter

from apps.datasets.services import get_all_datasets, get_dataset
from apps.datasets.dtos import DatasetDTO


api_router = APIRouter()


# @api_router.post("/items", response_model=schemas.Item)
# def create_item(item: schemas.ItemCreate):
#     item = models.Item.objects.create(**item.dict())

#     return item


@api_router.get("/datasets", response_model=List[DatasetDTO])
def read_all():
    datasets = get_all_datasets()
    return datasets


@api_router.get("/datasets/<dataset_id: int>", response_model=DatasetDTO)
def read(dataset_id):
    dataset = get_dataset(dataset_id)
    return dataset

def a:

