from uuid import uuid4
from django.db import models


class DatasetFile(models.Model):
    """ File model which stores dataset files """
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    upload = models.FileField(upload_to='apps/datasets/uploads')


class Dataset(models.Model):
    """ Information about dataset file internals """
    name = models.CharField(max_length=50)
    timestamp = models.DateTimeField(auto_now_add=True)
    height = models.IntegerField()
    width = models.IntegerField()
    comment = models.CharField(max_length=255, blank=True)
    file = models.OneToOneField(DatasetFile,
                                on_delete=models.CASCADE,
                                related_name="dataset")
