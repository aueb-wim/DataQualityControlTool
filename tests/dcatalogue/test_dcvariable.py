from __future__ import division
from __future__ import print_function
from __future__ import absolute_import
from __future__ import unicode_literals

import pytest
from unittest.mock import Mock
from mipqctool.dcatalogue import DcVariable
from mipqctool.config import ERROR

DCVAR1 = {
    'code': 'val1',
    'label': 'val 1',
    'sql_type': 'text',
    'type': 'text',
    'description': 'fe',
    'units': '',
    'methodology': 'few',
    'isCategorical': False
}

DCVAR2 = {
    'code': 'val2',
    'label': 'val 2',
    'sql_type': 'text',
    'type': 'multinominal',
    'description': 'fefw',
    'units': '',
    'methodology': 'feww',
    'isCategorical': True,
    'enumerations': [
        {'code': 'cat1', 'label': 'Cat 1'},
        {'code': 'cat2', 'label': 'Cat 2'}
    ]
}

DCVAR3 = {
    'code': 'val3',
    'label': 'val 3',
    'sql_type': 'int',
    'type': 'integer',
    'description': 'efew',
    'units': 'cm3',
    'methodology': '',
    'isCategorical': False,
    'maxValue': '30',
    'minValue': '0'
}

QCVAR1 = {
    'format': 'default',
    'name': 'val1',
    'title': 'val 1',
    'conceptPath': '/category/val1',
    'type': 'string',
    'MIPType': 'text',
    'description': 'fe',
}

QCVAR2 = {
    'format': 'default',
    'name': 'val2',
    'title': 'val 2',
    'conceptPath': '/category/val2',
    'type': 'string',
    'MIPType': 'nominal',
    'description': 'fefw',
    'constraints': {
        'enum': [
            'cat1',
            'cat2',
        ]
    }
}

QCVAR3 = {
    'format': 'default',
    'name': 'val3',
    'title': 'val 3',
    'conceptPath': '/category/val3',
    'type': 'integer',
    'MIPType': 'integer',
    'description': 'efew',
    'constraints': {
        'minimum': 0,
        'maximum': 30
    }
}
@pytest.mark.parametrize('dcdescriptor, result', [
    (DCVAR1, QCVAR1),
    (DCVAR2, QCVAR2),
    (DCVAR3, QCVAR3)
])
def test_createqcfield(dcdescriptor, result):
    node = Mock()
    node.conceptpath = '/category'
    testvariable = DcVariable(dcdescriptor, node)
    assert testvariable.createqcfield() == result


@pytest.mark.parametrize('dcdescriptor, result', [
    (DCVAR1, '/category/val1'),
])
def test_conceptpath(dcdescriptor, result):
    node = Mock()
    node.conceptpath = '/category'
    testvariable = DcVariable(dcdescriptor, node)
    assert testvariable.conceptpath == result
