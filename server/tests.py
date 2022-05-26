from pprint import pprint

import pytest
from django.db import IntegrityError, transaction
from pydantic import ValidationError

from .models import GoodTable, BadTable, StatsVendor


@pytest.fixture(autouse=True)
def set_test_settings(settings):
    settings.DEBUG = True


@pytest.fixture
def sample_good():
    good = GoodTable(name='name_sample', content='content_sample')
    good.save()
    return good


def test_model_save(transactional_db):
    record = GoodTable(name='name1', content='content1')
    with pytest.raises(ValueError) as e:
        record.save(force_update=True)
    assert e.value.args[0] == 'Cannot force an update in save() with no primary key.'

    record.save(force_insert=True)

    with pytest.raises(IntegrityError) as e:
        record.save(force_insert=True)
    assert e.value.args[0] == 'UNIQUE constraint failed: server_goodtable.id'


def test_foreign_key(transactional_db, sample_good):
    bad = BadTable()
    with pytest.raises(IntegrityError) as e:
        bad.save()
    assert (
        e.value.args[0] == 'NOT NULL constraint failed: server_badtable.good_table_id'
    )


def test_show_raw_sql(transactional_db, sample_good):
    from django.db import connection
    from django.db.models.query_utils import Q

    sample_good.name = 'my name sample'
    sample_good.save()

    assert len(connection.queries) == 2

    sample_good.save()
    assert len(connection.queries) == 3

    records = GoodTable.objects.all()[10:20]
    records.count()
    # trigger a limit offset sql
    assert len(connection.queries) == 4

    q = Q(name='A')
    q &= Q(name='B')
    # q is False condition
    records = GoodTable.objects.filter(q)
    assert records.count() == 0
    assert len(connection.queries) == 5


def test_ninja_schema():
    from metamap.api import CreateServerArgs, SearchServerArgs

    with pytest.raises(ValidationError):
        CreateServerArgs()

    with pytest.raises(ValidationError):
        CreateServerArgs(name='s1')

    CreateServerArgs(name='s1', ip='127.0.0.1')

    SearchServerArgs(name='s1')


def test_transaction(transactional_db):
    with pytest.raises(RuntimeError):
        with transaction.atomic():
            # avoid partial update
            StatsVendor.objects.create(vendor_id=1)
            StatsVendor.objects.create(vendor_id=2)
            raise RuntimeError('Simulate an error')
    assert StatsVendor.objects.count() == 0

    with transaction.atomic():
        StatsVendor.objects.create(vendor_id=1)
    assert StatsVendor.objects.count() == 1

    with pytest.raises(RuntimeError):
        # partial update without atomic
        StatsVendor.objects.create(vendor_id=2)
        StatsVendor.objects.create(vendor_id=3)
        raise RuntimeError('Simulate an error')

    assert StatsVendor.objects.count() == 3
