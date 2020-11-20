from django.db import models


class DatasetFile(models.Model):
    """ File storage model """
    upload = models.FileField(upload_to='apps/datasets/uploads/')


class Dataset(models.Model):
    """ Information about dataset file internals """
    name = models.CharField(max_length=50)
    timestamp = models.DateTimeField(auto_now_add=True)
    height = models.IntegerField()
    width = models.IntegerField()
    column_names = models.CharField(max_length=50)
    column_types = models.CharField(max_length=50)
    comment = models.CharField(max_length=255, blank=True)
    file = models.OneToOneField(DatasetFile,
                                on_delete=models.CASCADE,
                                related_name='dataset')
