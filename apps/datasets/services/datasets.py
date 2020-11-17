from typing import List, Optional

from apps.datasets.dtos import DatasetDTO
from apps.datasets.models import Dataset


def save_dataset(dataset_info: DatasetDTO) -> DatasetDTO:
    """ Save new dataset to DB model """
    dataset = Dataset.objects.create(**dataset_info.dict())
    return DatasetDTO.from_orm(dataset)


def get_dataset(dataset_id: int) -> Optional[DatasetDTO]:
    """ Get selected dataset from the DB model """
    try:
        dataset = Dataset.objects.get(pk=dataset_id)
    except Dataset.DoesNotExist:
        return None
    return DatasetDTO.from_orm(dataset)


def get_all_datasets() -> List[DatasetDTO]:
    """ Get all datasets from the DB """
    datasets = Dataset.objects.all()
    return [DatasetDTO.from_orm(d) for d in datasets]
