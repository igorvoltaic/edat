from uuid import uuid4
from django.db import models


class Dataset(models.Model):
    """ Information about dataset file internals """
    name = models.CharField(max_length=150)
    timestamp = models.DateTimeField(auto_now_add=True)
    height = models.IntegerField()
    width = models.IntegerField()
    comment = models.CharField(max_length=255, blank=True)


class DatasetFile(models.Model):
    """ File model which stores dataset files """
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    upload = models.FileField(upload_to='apps/datasets/uploads')
    dataset = models.OneToOneField(Dataset,
                                   on_delete=models.CASCADE, default=None,
                                   related_name="file", null=True)
