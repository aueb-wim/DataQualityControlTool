from __future__ import division
from __future__ import print_function
from __future__ import absolute_import
from __future__ import unicode_literals

import pytest
from copy import deepcopy
from mipqctool.config import ERROR
from mipqctool.model.qcfrictionless import QcTable
from mipqctool.model.qcfrictionless import QcSchema
from tableschema import Table
from mipqctool.tableprofiler import TableProfiler


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

SCHEMA_COMPLEX = {'fields': [
         {'name': 'id', 'type': 'integer', 'format': 'default',
          'MIPType': 'integer', 'bareNumber': True},
         {'name': 'visitid', 'type': 'integer', 'format': 'default',
          'MIPType': 'integer', 'bareNumber': True},
         {'name': 'name', 'type': 'string', 'format': 'default',
          'MIPType': 'text'},
         {'name': 'diagnosis', 'type': 'string', 'format': 'default',
          'MIPType': 'nominal', 'constraints': {'enum': ['AD', 'MCI', 'NL']}},
         {'name': 'presure', 'type': 'number', 'format': 'default',
          'MIPType': 'numerical', 'bareNumber': True},
         {'name': 'onlyone', 'type': 'integer', 'format': 'default',
          'MIPType': 'integer', 'bareNumber': False, 'suffix': ' #',
          'constraints': {'unique': True}},
        ],
      'missingValues': [''],
      }


@pytest.fixture
def simple_profiler():
    return TableProfiler(SCHEMA_SIMPLE)

# Tests


@pytest.mark.parametrize('row, result', [
    (['1', 'jyly', 'als'],
     ([{'name': 'id', 'value': 1, 'result': 'valid'},
       {'name': 'name', 'value': 'jyly', 'result': 'valid'},
       {'name': 'diagnosis', 'value': 'als', 'result': 'invalid'}],
      False, 0, [])),
    (['na', '', 'AD'],
     ([{'name': 'id', 'value': 'na', 'result': 'invalid'},
       {'name': 'name', 'value': None, 'result': 'na'},
       {'name': 'diagnosis', 'value': 'AD', 'result': 'valid'}],
      False, 1, [])),
    (['12', 'Judy', 'MCI', ''], ERROR),
])
def test_validate_row(row, result, simple_profiler):
    assert simple_profiler._validate_row(row, False) == result


@pytest.mark.parametrize('row, result', [
    (['5', 'john', 'AD'], ['name']),
    (['2', 'john', 'AD'], ['id', 'name']),
    (['2', 'tony', 'AD'], ['id']),
])
def test_validate_row_dublicate(row, result):
    schema = deepcopy(SCHEMA_SIMPLE)
    schema['primaryKey'] = 'id'
    schema['fields'][1]['constraints'] = {'unique': True}
    profiler = TableProfiler(schema)
    headers = ['id', 'name', 'diagnosis']
    rows = [
        ['1', 'john', 'AD'],
        ['2', 'mary', ''],
        ['3', 'george', 'MCI'],
        ['4', 'lisa', 'AD'],
    ]
    profiler.validate(rows, headers)
    test_result = set(profiler._validate_row(row, check_uniques=True)[3])
    assert test_result == set(result)


@pytest.mark.parametrize('path, schema, valid, rows_with_invalids', [
    ('tests/test_datasets/simple.csv', SCHEMA_SIMPLE, True, []),
    ('tests/test_datasets/integer.csv', SCHEMA_SIMPLE, False, []),
    ('tests/test_datasets/simple_invalid.csv', SCHEMA_SIMPLE, False, [7]),
    ('tests/test_datasets/complex_invalid.csv', SCHEMA_COMPLEX, False, [4, 7, 9]),
])
def test_vadidate_rows_with_invalids(path, schema, valid, rows_with_invalids):
    profiler = TableProfiler(schema)
    table = QcTable(path, schema=None)
    rows = table.read(cast=False)
    assert profiler.validate(rows, table.headers) == valid
    assert profiler.rows_with_invalids == rows_with_invalids


def test_invalid_rows():
    profiler = TableProfiler(SCHEMA_SIMPLE)
    table = QcTable('tests/test_datasets/simple_invalid_2.csv', schema=None)
    rows = table.read(cast=False)
    assert profiler.validate(rows, table.headers) == False
    assert profiler.invalid_rows == [5]


@pytest.mark.parametrize('path, schema, primary_keys, dublicates', [
    ('tests/test_datasets/simple_invalid.csv', SCHEMA_SIMPLE, 'id', [6]),
    ('tests/test_datasets/complex_invalid.csv', SCHEMA_COMPLEX, ['id'], [4, 6]),
    ('tests/test_datasets/complex_invalid.csv', SCHEMA_COMPLEX, ['id', 'visitid'], [4]),
])
def test_dublicates(path, schema, primary_keys, dublicates):
    schema['primaryKey'] = primary_keys
    profiler = TableProfiler(schema)
    table = QcTable(path, schema=None)
    rows = table.read(cast=False)
    profiler.validate(rows, table.headers)
    assert profiler.rows_with_dublicates == dublicates


@pytest.mark.parametrize('path, schema, primary_keys, missing_pk, missing_rq', [
    ('tests/test_datasets/complex_invalid.csv', SCHEMA_COMPLEX, ['id'], [], [8]),
    ('tests/test_datasets/complex_invalid.csv', SCHEMA_COMPLEX, ['id', 'visitid'], [9], [8]),
])
def test_missing(path, schema, primary_keys, missing_pk, missing_rq):
    schema['primaryKey'] = primary_keys
    schema['missingValues'].append('NA')
    schema['fields'][2]['constraints'] = {'required': True}
    profiler = TableProfiler(schema)
    table = QcTable(path, schema=None)
    rows = table.read(cast=False)
    profiler.validate(rows, table.headers)
    assert profiler.rows_with_missing_pk == missing_pk
    assert profiler.rows_with_missing_required == missing_rq
