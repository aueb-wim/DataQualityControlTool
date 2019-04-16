from __future__ import division
from __future__ import print_function
from __future__ import absolute_import
from __future__ import unicode_literals

import pytest
from mock import Mock, patch
from mipqctool.qctable import QcTable


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
    s = QcTable('data/empty.csv')
    d = s.infer()
    assert d == {
        'fields': [],
        'missingValues': [''],
    }


@pytest.mark.parametrize('path, schema', [
    ('data/simple.csv', SCHEMA_SIMPLE),
    ])
def test_schema_infer_tabulator(path, schema):
    table = QcTable(path)
    table.infer(maxlevels=3)
    assert table.headers == ['id', 'name', 'diagnosis']
    assert table.schema.descriptor == schema


@patch('tableschema.storage.import_module')
def test_schema_infer_storage(import_module, apply_defaults):
    import_module.return_value = Mock(Storage=Mock(return_value=Mock(
        describe=Mock(return_value=SCHEMA_MIN),
        iter=Mock(return_value=DATA_MIN[1:]),
    )))
    table = QcTable('table', storage='storage')
    table.infer()
    assert table.headers == ['key', 'value']
    assert table.schema.descriptor == apply_defaults(SCHEMA_MIN)
