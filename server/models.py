from django.db import models


# Create your models here.
class GoodTable(models.Model):
    name = models.CharField(max_length=40, unique=True)
    content = models.TextField(default='')


class BadProfile(models.Model):
    address = models.CharField(max_length=128)
    birthday = models.DateField(auto_now=True)


class BadTable(models.Model):
    good_table = models.ForeignKey(
        GoodTable,
        on_delete=models.CASCADE,
        related_name='bad_tables',
        db_constraint=False,
    )
    change_time = models.DateTimeField(auto_now_add=True)
    profile = models.OneToOneField(
        BadProfile,
        on_delete=models.CASCADE,
        related_name='profile_bad_table',
        blank=True,
        null=True,
    )


class Server(models.Model):
    name = models.CharField(max_length=64)
    ip = models.CharField(max_length=128)
    date_added = models.DateTimeField(auto_now_add=True)
    date_change = models.DateTimeField(auto_now=True)
