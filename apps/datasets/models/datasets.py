from django.db import models


class Dataset(models.Model):
    name = models.CharField(max_length=50)
    timestamp = models.DateTimeField(auto_now_add=True)
    height = models.IntegerField()
    width = models.IntegerField()
    comment = models.CharField(max_length=255, blank=True)
