import pytest
from django.db import IntegrityError, transaction, connections
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


def test_foreign_key(transactional_db, sample_good):
    bad = BadTable()
    with pytest.raises(IntegrityError) as e:
        bad.save()


def test_show_raw_sql(transactional_db, sample_good):
    from django.db import connection
    from django.db.models.query_utils import Q

    sample_good.name = 'my name sample'
    sample_good.save()

    sql_count = len(connection.queries)

    sample_good.save()
    assert len(connection.queries) == sql_count + 1
    sql_count += 1

    records = GoodTable.objects.all()[10:20]
    records.count()
    # trigger a limit offset sql
    assert len(connection.queries) == sql_count + 1
    sql_count += 1

    q = Q(name='A')
    q &= Q(name='B')
    # q is False condition
    records = GoodTable.objects.filter(q)
    assert records.count() == 0
    assert len(connection.queries) == sql_count + 1
    sql_count += 1


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


def test_transaction_with_raw_sql(transactional_db):
    conn = connections['default']
    with pytest.raises(RuntimeError):
        with transaction.atomic():
            with conn.cursor() as cursor:
                cursor.execute('INSERT INTO server_statsvendor (vendor_id) VALUES (10)')
                cursor.execute('INSERT INTO server_statsvendor (vendor_id) VALUES (20)')
                raise RuntimeError

    assert StatsVendor.objects.count() == 0

    with pytest.raises(RuntimeError):
        with conn.cursor() as cursor:
            cursor.execute('INSERT INTO server_statsvendor (vendor_id) VALUES (10)')
            cursor.execute('INSERT INTO server_statsvendor (vendor_id) VALUES (20)')
            raise RuntimeError

    assert StatsVendor.objects.count() == 2

    with transaction.atomic():
        with conn.cursor() as cursor:
            cursor.execute('DELETE FROM server_statsvendor')
            cursor.execute('INSERT INTO server_statsvendor (vendor_id) VALUES (10)')
    assert StatsVendor.objects.count() == 1
    conn.close()


def test_db_connection(transactional_db):
    from django.db.backends.mysql.base import DatabaseWrapper

    conn: DatabaseWrapper = connections['default']
    with conn.cursor() as cursor:
        cursor.execute('SELECT * FROM server_statsvendor')
    conn.close()

    conn: DatabaseWrapper = connections['default']
    with conn.cursor() as cursor:
        cursor.execute('SELECT * FROM server_statsvendor')
    conn.close()
