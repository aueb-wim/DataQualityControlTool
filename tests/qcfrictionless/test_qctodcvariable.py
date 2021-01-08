from __future__ import division
from __future__ import print_function
from __future__ import absolute_import
from __future__ import unicode_literals

import pytest

from mipqctool.qcfrictionless.qctodc import QctoDCVariable

NUMERICAL_DESC = {
    'name': 'testvar',
    'format': 'default',
    'type': 'number',
    'MIPType': 'numerical',
    'constraints': {
        'minimum': 0,
        'maximum': 10
        }
}

NOMINAL_DESC = {
    'name': 'testvar',
    'format': 'default',
    'type': 'string',
    'MIPType': 'nominal',
    'constraints': {
        'enum': ['Cat1', 'Cat2', 'Anot3']
    }
}

NUMERICAL_DC = {
    'csvFile': 'file.csv',
    'name': 'testvar',
    'code': 'testvar',
    'type': 'real',
    'values': '0-10',
    'unit': '',
    'canBeNull': 'Y',
    'description': None,
    'comments': '',
    'conceptPath': '/root',
    'methodology': '',
    'sql_type': 'number',
    'cde': None
    }

NOMINAL_DC = {
    'csvFile': 'file.csv',
    'name': 'testvar',
    'code': 'testvar',
    'type': 'nominal',
    'values': '{"Cat1","Cat1"},{"Cat2","Cat2"},{"Anot3","Anot3"}',
    'unit': '',
    'canBeNull': 'Y',
    'description': None,
    'comments': '',
    'conceptPath': '/root',
    'methodology': '',
    'sql_type': 'string',
    'cde': None
    }

@pytest.mark.parametrize('qcdesc, result', [
    (NUMERICAL_DESC, NUMERICAL_DC),
    (NOMINAL_DESC, NOMINAL_DC)
])
def test_info(qcdesc, result):
    test = QctoDCVariable(qcdesc, 'file.csv', '/root')
    assert test.info == result