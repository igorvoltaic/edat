from apps.datasets.dtos import DatasetDTO
from apps.datasets.models import Dataset
from typing import List


def save_dataset(dataset_info: DatasetDTO) -> DatasetDTO:
    """ Save new dataset to DB model """
    dataset = Dataset.objects.create(
        name=dataset_info.name,
        height=dataset_info.height,
        width=dataset_info.width,
        comment=dataset_info.comment
    )
    return DatasetDTO.from_orm(dataset)


def get_dataset(dataset_id: int) -> DatasetDTO:
    """ Get selected dataset from the DB model """
    dataset = Dataset.objects.get(pk=dataset_id)
    return DatasetDTO.from_orm(dataset)


def get_all_datasets() -> List[DatasetDTO]:
    """ Get all datasets from the DB """
    datasets = Dataset.objects.all()
    return [DatasetDTO.from_orm(d) for d in datasets]
