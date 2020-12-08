""" Dataset app models layer
"""
from django.db import models
from django_enum_choices.fields import EnumChoiceField

from apps.datasets.dtos import ColumnType


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
    datatype = EnumChoiceField(ColumnType)
