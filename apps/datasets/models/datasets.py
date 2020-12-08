""" Dataset app models layer
"""
from django.db import models
from helpers import get_datatype_choises


class Dataset(models.Model):
    """ Information about dataset file internals """
    name = models.CharField(max_length=150)
    timestamp = models.DateTimeField(auto_now_add=True)
    height = models.IntegerField()
    width = models.IntegerField()
    comment = models.CharField(max_length=255, blank=True)
    file = models.FileField(null=True)
    indexes = [
        models.Index(fields=['-timestamp']),
        models.Index(fields=['name']),
    ]


class Column(models.Model):
    """ Column datatypes, names and indexes associated with dataset """
    dataset = models.ForeignKey(
        Dataset,
        on_delete=models.CASCADE,
        related_name="columns"
    )
    index = models.IntegerField()
    name = models.CharField(max_length=50, blank=True)
    DATATYPE_CHOICES = get_datatype_choises()
    datatype = models.CharField(choices=DATATYPE_CHOICES, max_length=8)
