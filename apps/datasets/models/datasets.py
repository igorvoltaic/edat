from django.db import models


class Dataset(models.Model):
    name = models.CharField(max_length=50)
    timestamp = models.DateTimeField(auto_created=True)
    height = models.IntegerField(max_length=5)
    width = models.IntegerField(max_length=5)
    comment = models.CharField(max_length=255, blank=True)
