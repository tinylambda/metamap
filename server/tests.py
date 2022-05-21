import pytest
from django.db import IntegrityError

from .models import GoodTable, BadTable


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
    sample_good.name = 'my name sample'
    sample_good.save()
    from django.db import connection

    print(connection.queries)
