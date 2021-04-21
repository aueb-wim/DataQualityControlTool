from __future__ import division
from __future__ import print_function
from __future__ import absolute_import
from __future__ import unicode_literals

import pytest
from mipqctool.model.qcfrictionless.cde import CdeVariable
from mipqctool.config import ERROR

CDE_NOMINAL1 = {
    'code': 'gender  ', 'cdetype': ' nominaL',  'conceptpath': '/cde/gender',
    'mipvalues': '{"M", "Male"},{"F", "Female"}', 'variable_lookup': '"Sex","sex", " gendre"',
    'enum_lookup': '{"M","Homme", "Male", "H"},{"F","Femme", "Female"}'
}

CDE_INTEGER1 = {
    'code': 'age', 'cdetype': 'integer', 'conceptpath': '/cde/age',
    'mipvalues': '0-120',
    'variable_lookup': '"Age", "age_value", "âge", "ηλικία"',
    'enum_lookup': None
}

CDE_NOMINAL_COLORS = {
    'code': 'Colors', 'cdetype': ' nominal',  'conceptpath': '/cde/sex',
    'mipvalues': '{"B", "Black"},{"W", "White"}, {"R", "Red"},{"BL","Blue"}', 
    'variable_lookup': '"Colours", "Colore", " Χρώματα"',
    'enum_lookup': '{"Μαύρο","Negro"},{"Άσπρο, "Blanco"},{"Κόκκινο", "Rossa"}'
}

@pytest.mark.parametrize('cde_strs, result', [
    (CDE_NOMINAL1, {
        'code': 'gender',
        'miptype': 'nominal',
        'conceptpath': '/cde/gender',
        'mipvalue': ['M', 'F'],
        'variable_lookup': ['gendre', 'sex'],
        'enum_lookups': ['f', 'female', 'femme', 'h', 'homme', 'm', 'male']
    }),
    (CDE_INTEGER1, {
        'code': 'age',
        'miptype': 'integer',
        'conceptpath': '/cde/age',
        'mipvalue': [0.0, 120.0],
        'variable_lookup': ['age', 'age_value', 'âge', 'ηλικία'],
    })
])
def test_cdeproperties(cde_strs, result):
    test = CdeVariable(**cde_strs)
    with pytest.warns(None) as recorded:
        assert test.code == result['code']
        assert test.conceptpath == result.get('conceptpath')
        assert test.mipvalues == result.get('mipvalue')
        assert test.variable_lookup == result.get('variable_lookup')
        assert test.enum_lookup == result.get('enum_lookups')
        assert recorded.list == []



@pytest.mark.parametrize('cdevar, result', [
    (CDE_NOMINAL_COLORS, ['B', 'W', 'R', 'BL'])
])
def test_cdevariable_mapvalues(cdevar, result):
    test = CdeVariable(**cdevar)

    assert test.mipvalues == result

@pytest.mark.parametrize('value, cdevar, result', [
    ('negros', CDE_NOMINAL_COLORS, 'B'),
    ('rossa', CDE_NOMINAL_COLORS, 'R')
])
def test_cdevariable_suggest_replacment(value, cdevar, result):
    test = CdeVariable(**cdevar)
    totest = test.suggest_value(value, threshold=0.6)
    assert totest == result