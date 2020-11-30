from uuid import uuid4
from django.db import models


class Dataset(models.Model):
    """ Information about dataset file internals """
    name = models.CharField(max_length=150)
    timestamp = models.DateTimeField(auto_now_add=True)
    height = models.IntegerField()
    width = models.IntegerField()
    comment = models.CharField(max_length=255, blank=True)
    file = models.FileField(upload_to='apps/datasets/uploads')


class Column(models.Model):
    """ Column datatypes, names and indexes associated with dataset """
    dataset= models.ForeignKey(Dataset, on_delete=models.CASCADE, related_name="columns")
    index = models.IntegerField()
    name = models.CharField(max_length=50, blank=True)
    datatype = models.CharField(max_length=50, blank=True)

