from django.db import models


class DataSource(models.Model):
    name = models.CharField("Data source name", max_length=128)
