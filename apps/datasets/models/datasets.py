""" Dataset app models layer
"""
from django.db import models
from django_enum_choices.fields import EnumChoiceField

from apps.datasets.dtos import ColumnType, Delimiter, Quotechar, PlotType
from django_celery_results.models import TaskResult


class Dataset(models.Model):
    """ Information about dataset file internals """
    name = models.CharField(max_length=150)
    timestamp = models.DateTimeField(auto_now_add=True)
    height = models.IntegerField()
    width = models.IntegerField()
    comment = models.CharField(max_length=255, blank=True)
    file = models.FileField(null=True)

    class Meta:
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['-timestamp']),
            models.Index(fields=['name']),
        ]


class CsvDialect(models.Model):
    """ CSV file delimiter, quotechar and has_header information """
    dataset = models.OneToOneField(
        Dataset,
        on_delete=models.CASCADE,
        related_name="csv_dialect"
    )
    delimiter = EnumChoiceField(Delimiter)
    quotechar = EnumChoiceField(Quotechar)
    has_header = models.BooleanField()
    start_row = models.IntegerField(null=True)


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


class Plot(models.Model):
    dataset = models.ForeignKey(
        Dataset,
        on_delete=models.CASCADE,
        related_name="plots"
    )
    timestamp = models.DateTimeField(auto_now_add=True, null=True)
    plot_type = EnumChoiceField(PlotType)
    checksum = models.CharField(max_length=32)
    height = models.IntegerField()
    width = models.IntegerField()
    columns = models.ManyToManyField('Column', db_index=True)
    params = models.JSONField()
    file = models.FileField(null=True)
    task_id = models.CharField(max_length=255, unique=True, null=True)

    class Meta:
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['-timestamp']),
            models.Index(fields=['checksum']),
            models.Index(fields=['task_id']),
        ]
