from __future__ import division
from __future__ import print_function
from __future__ import absolute_import
from __future__ import unicode_literals

import pytest
from datetime import datetime
from mipqctool.qcfield import QcField
from mipqctool.config import ERROR
from mipqctool.exceptions import DataTypeError, ConstraintViolationError

MISSING_VALUES = ['']
DATE_DESC = {'name': 'testvar',
             'type': 'date',
             'format': 'default',
             'MIPType': 'date'}
NOMINAL_DESC = {'name': 'testvar',
                'format': 'default',
                'type': 'string',
                'MIPType': 'nominal',
                'constraints': {
                    'enum': ['Cat1', 'Cat2', 'Cat3']
                }}
NUMERICAL_DESC = {'name': 'testvar',
                  'format': 'default',
                  'type': 'number',
                  'MIPType': 'numerical',
                  'constraints': {
                      'minimum': 0,
                      'maximum': 10
                      }
                  }

INTEGER_DESC = {'name': 'testvar',
                'format': 'default',
                'type': 'integer',
                'MIPType': 'integer',
                'constraints': {
                    'minimum': 3,
                    'maximum': 5
                    }
                }


@pytest.mark.parametrize('descriptor, value', [
    (DATE_DESC, 'NOTDATE'),
    (DATE_DESC, '123'),
    (DATE_DESC, '12-3-2018'),
    (NUMERICAL_DESC, 'NOTNUMBER'),
    (INTEGER_DESC, '1.23'),
    (INTEGER_DESC, '2.5')
])
def test_validate_DataTypeException(descriptor, value):
    testfield = QcField(descriptor, missing_values=MISSING_VALUES)
    with pytest.raises(DataTypeError):
        testfield.validate(value)


@pytest.mark.parametrize('descriptor, value', [
    (INTEGER_DESC, '-1'),
    (NUMERICAL_DESC, '10.4'),
    (NOMINAL_DESC, 'CAT1')
])
def test_validate_ConstraintException(descriptor, value):
    testfield = QcField(descriptor)
    with pytest.raises(ConstraintViolationError):
        testfield.validate(value)


@pytest.mark.parametrize('descriptor, value, result', [
    (DATE_DESC, '2019-12-12', '2019-12-12'),
    (NUMERICAL_DESC, '3.1', '3.1'),
    (INTEGER_DESC, '3', '3'),
    (NOMINAL_DESC, 'Cat2', 'Cat2')
])
def test_validate(descriptor, value, result):
    testfield = QcField(descriptor)
    with pytest.warns(None) as recorded:
        assert testfield.validate(value) == result
        assert recorded.list == []


@pytest.mark.parametrize('descriptor, value, result', [
    (INTEGER_DESC, '1', 'NA'),
    (NOMINAL_DESC, 'CAT2', 'Cat2'),
    (DATE_DESC, '31-5-1980', 'NA'),
    (DATE_DESC, '31 May 1980', 'NA'),
    (NUMERICAL_DESC, '-10.14', 'NA')
])
def test_suggestc(descriptor, value, result):
    testfield = QcField(descriptor, missing_values=['NA'])
    with pytest.warns(None) as recorded:
        assert testfield.suggestc(value) == result
        assert recorded.list == []


@pytest.mark.parametrize('descriptor, value, result', [
    (INTEGER_DESC, 'notnumber', ''),
    (NOMINAL_DESC, 32, ''),
    (DATE_DESC, '31-5-1980', '1980-05-31'),
    (DATE_DESC, '31 May 1980', '1980-05-31'),
    (NUMERICAL_DESC, 'nonono', ''),
    (INTEGER_DESC, '3.5', '3'),
    (INTEGER_DESC, '1.23', ''),
    (INTEGER_DESC, '2.5', ''),
    (INTEGER_DESC, '5.4', '5')
])
def test_suggestd(descriptor, value, result):
    testfield = QcField(descriptor)
    with pytest.warns(None) as recorded:
        assert testfield.suggestd(value) == result
        assert recorded.list == []
