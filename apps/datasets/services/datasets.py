from apps.datasets.dtos import DatasetDTO, DatasetDTOList
from apps.datasets.models import Dataset
from typing import List


def save_dataset(dataset_info: DatasetDTO) -> DatasetDTO:
    """ Save new dataset to DB model """
    Dataset.objects.create(
        name=dataset_info.name,
        height=dataset_info.height,
        width=dataset_info.width,
        comment=dataset_info.comment
    )


def get_dataset(dataset_id: int) -> DatasetDTO:
    """ Get selected dataset from the DB model """
    dataset = Dataset.objects.get(pk=dataset_id)
    dto = DatasetDTO.from_orm(dataset)
    return dto


def get_all_datasets() -> List[DatasetDTO]:
    datasets = Dataset.objects.all()
    dto_list = [DatasetDTO.from_orm(d).dict() for d in datasets]
    dtos = DatasetDTOList.parse_obj(dto_list)
    return dtos
