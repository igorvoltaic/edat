from typing import List
from fastapi import APIRouter

from datasets import services

api_router = APIRouter()


# @api_router.post("/items", response_model=schemas.Item)
# def create_item(item: schemas.ItemCreate):
#     item = models.Item.objects.create(**item.dict())

#     return item


@api_router.get("/items", response_model=List[DatasetDTO])
def read_items():
    datasets = get_all_datasets()
    return datasets
