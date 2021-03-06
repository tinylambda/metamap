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


class StatsVendor(models.Model):
    vendor_id = models.IntegerField(null=True, db_index=True)
    total_earned = models.FloatField(null=True)
    project_count = models.BigIntegerField(null=True, default=0)
    project_not_complete_count = models.BigIntegerField(null=True, default=0)
    ongoing_tickets = models.BigIntegerField(null=True, default=0)

    def __str__(self):
        return f'StatsVendor(vendor_id={self.vendor_id})'
