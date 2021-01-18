from __future__ import division
from __future__ import print_function
from __future__ import absolute_import
from __future__ import unicode_literals

import pytest
import csv
from unittest.mock import Mock, patch
from mipqctool.model.qcfrictionless import QcTable
from mipqctool.exceptions import QCToolException


DATA_MIN = [('key', 'value'), ('one', '1'), ('two', '2')]
SCHEMA_MIN = {'fields': [{'name': 'key', },
                         {'name': 'value', 'type': 'integer',
                          'MIPType': 'integer', 'bareNumber': True}],
              }

SCHEMA_SIMPLE = {'fields': [
         {'name': 'id', 'type': 'integer', 'format': 'default',
          'MIPType': 'integer', 'bareNumber': True},
         {'name': 'name', 'type': 'string', 'format': 'default',
          'MIPType': 'text'},
         {'name': 'diagnosis', 'type': 'string', 'format': 'default',
          'MIPType': 'nominal', 'constraints': {'enum': ['AD', 'MCI', 'NL']}},
        ],
      'missingValues': ['']
      }


# Tests


def test_infer_schema_empty_file():
    s = QcTable('tests/test_datasets/empty.csv', schema=None)
    d = s.infer()
    assert d == {
        'fields': [],
        'missingValues': [''],
    }


@pytest.mark.parametrize('path, schema', [
    ('tests/test_datasets/simple.csv', SCHEMA_SIMPLE),
    ])
def test_schema_infer_tabulator(path, schema):
    table = QcTable(path, schema=None)
    table.infer(maxlevels=3)
    assert table.headers == ['id', 'name', 'diagnosis']
    assert table.schema.descriptor == schema


@patch('tableschema.storage.import_module')
def test_schema_infer_storage(import_module, apply_defaults):
    import_module.return_value = Mock(Storage=Mock(return_value=Mock(
        describe=Mock(return_value=SCHEMA_MIN),
        iter=Mock(return_value=DATA_MIN[1:]),
    )))
    table = QcTable('table', schema=None, storage='storage')
    table.infer()
    assert table.headers == ['key', 'value']
    assert table.schema.descriptor == apply_defaults(SCHEMA_MIN)


@pytest.mark.parametrize('path, column_name', [
    ('tests/test_datasets/simple.csv', 'name'),
    ('tests/test_datasets/simple.csv', 'id')
])
def test_column_values(path, column_name):
    with open(path) as csvfile:
        reader = csv.reader(csvfile)
        #read header
        headers = next(reader)
        index = headers.index(column_name)
        result = [row[index] for row in reader]
        table = QcTable(path, schema=None)
        table.infer()
        assert table.column_values(column_name) == result


@pytest.mark.parametrize('path, column_name', [
    ('tests/test_datasets/simple.csv', 'non_exist_column'),
    ('tests/test_datasets/simple.csv', 'on exist column with spaces')
])
def test_column_values_exception(path, column_name):
    table = QcTable(path, schema=None)
    table.infer()
    with pytest.raises(QCToolException):
        assert table.column_values(column_name)

@pytest.mark.parametrize('path, result', [
    (
        'tests/test_datasets/simple.csv',
        ['id', 'name', 'diagnosis']
    ),
    (
        'tests/test_datasets/test_dataset.csv',
        ['Patient_id', 'Diagnosis Categories', 'Gender_num', 'Date_visit']
    ),

])
def test_actual_headers(path, result):
    table = QcTable(path, schema=None)
    assert table.actual_headers == result
