from __future__ import division
from __future__ import print_function
from __future__ import absolute_import
from __future__ import unicode_literals

import pytest
from mipqctool.qcfrictionless.qctodc import QCtoDC
from mipqctool.config import LOGGER

QCDESC1={
    'fields': [
        {'format': 'default', 'name': 'id', 'type': 'integer',
            'MIPType': 'integer', 'bareNumber': True},
        {'format': 'default', 'name': 'iq', 'type': 'number',
            'MIPType': 'numerical', 'decimalChar': '.',
            'bareNumber': True},
        {'name': 'testvar', 'format': 'default', 'type': 'number',
         'MIPType': 'numerical',
         'constraints': {'minimum': 0, 'maximum': 10}},
        {'name': 'testvar2', 'format': 'default',
         'type': 'string', 'MIPType': 'nominal',
         'constraints': {'enum': ['Cat1', 'Cat2', 'Anot3']}}
    ]
}

def test_export2csv():
    test = QCtoDC(QCDESC1, 'default.csv')
    test.export2csv('tests/test_datasets/exporttest.csv')

def test_export2excel():
    test = QCtoDC(QCDESC1, 'default.csv')
    test.export2excel('tests/test_datasets/exporttest.xlsx')
