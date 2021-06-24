from __future__ import division
from __future__ import print_function
from __future__ import absolute_import
from __future__ import unicode_literals

import pytest
from random import choice
from tests.mocker import ResultMocker
from mipqctool.model.qcfrictionless.qcschema import QcSchema, _QcTypeGuesser, _QcTypeResolver
from mipqctool.config import ERROR


@pytest.fixture
def qcshema():
    """Returns a QcSchema object"""
    return QcSchema()


@pytest.fixture
def guesser():
    """Returns a _QcTypeGuesser object"""
    return _QcTypeGuesser()


@pytest.fixture
def resolver():
    """Returns a _QCTypeResolver object"""
    return _QcTypeResolver()


# Tests

@pytest.mark.parametrize('value, result', [
    ('13', ('integer', 'd', 1)),
    (12.2, ('numerical', 'd.', 2)),
    ('123longsuffix1234', ('text', 'text', 3)),
    ('N/A', ('text', 'nan', 3)),
    ('12/12/2013', ('date', '%d/%m/%Y', 0)),
    ('', ('text', 'nan', 3))
])
def test_guesser(guesser, value, result):
    with pytest.warns(None) as recorded:
        assert guesser.infer(value) == result
        assert recorded.list == []


@pytest.mark.parametrize('counts, result', [
    ({'number': 6, 'nan': 3},
     {'type': 'number', 'format': 'default',
      'MIPType': 'numerical', 'decimalChar': '.',
      'bareNumber': True}),
    ({'date': 4, 'number': 2, 'integer': 2, 'nan': 10},
     {'type': 'date', 'format': '%d/%m/%Y',
      'MIPType': 'date'}),
    ({'number': 6, 'date': 5, 'nan': 15},
     {'type': 'date', 'format': '%d/%m/%Y',
      'MIPType': 'date'}),
    ({'number': 8, 'text': 10, 'nan': 2200},
     {'type': 'number', 'format': 'default',
      'MIPType': 'numerical', 'decimalChar': '.',
      'bareNumber': True}),
    ({'number': 8, 'text': 11, 'nan': 202},
     {'type': 'string', 'format': 'default',
      'MIPType': 'text'}),
    ({'integer': 10},
     {'type': 'integer', 'format': 'default',
      'MIPType': 'integer', 'bareNumber': True}),
    ({'number': 1, 'nan': 5200},
     {'type': 'number', 'format': 'default',
      'MIPType': 'numerical', 'decimalChar': '.',
      'bareNumber': True}),
])
def test_resolver(resolver, counts, result):
    mocker = ResultMocker()
    with pytest.warns(None) as recorded:
        uniques = set(['1.2', '21.2', '12.3', '11.3'])
        results = mocker.get_results(1, counts)
        assert resolver.get(results, uniques, 3, 0.75) == result
        assert recorded.list == []


@pytest.mark.parametrize('data, result', [
        ([
          ['id', 'age', 'name', 'birthdate', 'iq', 'gender'],
          ['1', '39y', 'Paul', '12/1/1945', '32.2', '1'],
          ['2', '23y', 'Jimmy', '11/5/2001', '0.5', '0'],
          ['3', '36y', 'Jane', '15/11/1955', '2.55', '1'],
          ['4', 'NA', 'Judy', '25/7/1961', '55.23', '1'],
          ['5', '41y', 'NA', '11/12/1951', '3.1', '0'],
         ], {
            'fields': [
                {'format': 'default', 'name': 'id', 'type': 'integer',
                 'MIPType': 'integer', 'bareNumber': True},
                {'format': 'default', 'name': 'age', 'type': 'integer',
                 'MIPType': 'integer', 'bareNumber': False,
                 'suffix': 'y'},
                {'format': 'default', 'name': 'name', 'type': 'string',
                 'MIPType': 'text'},
                {'format': '%d/%m/%Y', 'name': 'birthdate', 'type': 'date',
                 'MIPType': 'date'},
                {'format': 'default', 'name': 'iq', 'type': 'number',
                 'MIPType': 'numerical', 'decimalChar': '.',
                 'bareNumber': True},
                {'format': 'default', 'name': 'gender', 'type': 'boolean',
                 'MIPType': 'nominal', 'trueValues': ['1'],
                 'falseValues': ['0']},
            ],
            'missingValues': ['', 'NA']
        }),
        ([
          ['id', 'age', 'name', 'birthdate', 'iq', 'gender'],
          ['1', '39y', 'Paul', '12/1/1945', '32.2', '1'],
          ['2', '23y', 'Jimmy', '11/5/2001'],
          ['3', '36y', 'Jane', '15/11/1955', '2.55', '1'],
          ['4', '37', 'Judy', '25/7/1961', '55.23', '1'],
          ['5', '41y', 'Lore', '11/12/1951', '3.1', '0'],
         ], {
            'fields': [
                {'format': 'default', 'name': 'id', 'type': 'integer',
                 'MIPType': 'integer', 'bareNumber': True},
                {'format': 'default', 'name': 'age', 'type': 'integer',
                 'MIPType': 'integer', 'bareNumber': False,
                 'suffix': 'y'},
                {'format': 'default', 'name': 'name', 'type': 'string',
                 'MIPType': 'text'},
                {'format': '%d/%m/%Y', 'name': 'birthdate', 'type': 'date',
                 'MIPType': 'date'},
                {'format': 'default', 'name': 'iq', 'type': 'number',
                 'MIPType': 'numerical', 'decimalChar': '.',
                 'bareNumber': True},
                {'format': 'default', 'name': 'gender', 'type': 'boolean',
                 'MIPType': 'nominal', 'trueValues': ['1'],
                 'falseValues': ['0']},
            ],
            'missingValues': ['']
        }),
        ([
          ['id', 'age'],
          ['1', '39y', 'Paul', '12/1/1945', '32.2', '1'],
          ['2', '23y', 'Jimmy', '11/5/2001'],
          ['3', '36y', 'Jane', '15/11/1955', '2.55', '1'],
          ['4', '36', 'Judy', '25/7/1961', '55.23', '1'],
          ['5', '41y', 'NA', '11/12/1951', '3.1', '0'],
         ], {
            'fields': [
                {'format': 'default', 'name': 'id', 'type': 'integer',
                 'MIPType': 'integer', 'bareNumber': True},
                {'format': 'default', 'name': 'age', 'type': 'integer',
                 'MIPType': 'integer', 'bareNumber': False,
                 'suffix': 'y'}
            ],
            'missingValues': ['']
        }),
])
def test_infer(qcshema, data, result):
    qcshema.infer(data, maxlevels=3)
    assert qcshema.descriptor == result

@pytest.mark.parametrize('data, result', [
        ([
          ['id', 'age', 'name', 'birthdate', 'iq', 'gender'],
          ['1', '39y', 'Paul', '12/1/1945', '32.2', '1'],
          ['2', '23y', 'Jimmy', '11/5/2001', '0.5', '0'],
          ['3', '36y', 'Jane', '15/11/1955', '2.55', '1'],
          ['4', 'NA', 'Judy', '25/7/1961', '55.23', '1'],
          ['5', '41y', 'NA', '11/12/1951', '3.1', '0'],
         ], {
            'fields': [
                {'format': 'default', 'name': 'id', 'type': 'integer',
                 'MIPType': 'integer', 'bareNumber': True},
                {'format': 'default', 'name': 'age', 'type': 'integer',
                 'MIPType': 'integer', 'bareNumber': False,
                 'suffix': 'y'},
                {'format': 'default', 'name': 'name', 'type': 'string',
                 'MIPType': 'text'},
                {'format': '%d/%m/%Y', 'name': 'birthdate', 'type': 'date',
                 'MIPType': 'date'},
                {'format': 'default', 'name': 'iq', 'type': 'number',
                 'MIPType': 'numerical', 'decimalChar': '.',
                 'bareNumber': True},
                {'format': 'default', 'name': 'gender', 'type': 'boolean',
                 'MIPType': 'nominal', 'trueValues': ['1'],
                 'falseValues': ['0']},
            ],
            'missingValues': ['']
        })
])
def test_infer_na(qcshema, data, result):
    qcshema.infer(data, maxlevels=3, na_empty_strings_only=True)
    assert qcshema.descriptor == result
