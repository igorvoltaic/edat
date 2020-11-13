from apps.datasets.dtos import DatasetDTO
from apps.datasets.models import Dataset


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
    return DatasetDTO(
                id=dataset.id,
                name=dataset.name,
                timestamp=dataset.timestamp,
                height=dataset.height,
                width=dataset.width,
                comment=dataset.comment
            )

def get_all_datasets() -> List:
    datasets = Dataset.objects.get(pk=dataset_id)

