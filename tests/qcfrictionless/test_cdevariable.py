from __future__ import division
from __future__ import print_function
from __future__ import absolute_import
from __future__ import unicode_literals

import pytest
from mipqctool.model.qcfrictionless.cde import CdeVariable
from mipqctool.config import ERROR

CDE_NOMINAL1 = [
    'gender  ', ' nominaL', ' /cde/gender',
    '{"M", "Male"},{"F", "Female"}', '"Sex","sex", " gendre"',
    '{"M","Homme", "Male", "H"},{"F","Femme", "Female"}'
]

CDE_INTEGER1 = [
    'age', 'integer', '/cde/age',
    '0-120',
    '"Age", "age_value", "âge", "ηλικία"', None
]

@pytest.mark.parametrize('cde_strs, result', [
    (CDE_NOMINAL1, {
        'code': 'gender',
        'miptype': 'nominal',
        'conceptpath': '/cde/gender',
        'mipvalue': ['f', 'm'],
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
    test = CdeVariable(code=cde_strs[0], cdetype=cde_strs[1],
                       conceptpath=cde_strs[2], mipvalues=cde_strs[3],
                       variable_lookup=cde_strs[4], enum_lookup=cde_strs[5])
    with pytest.warns(None) as recorded:
        assert test.code == result['code']
        assert test.conceptpath == result.get('conceptpath')
        assert test.mipvalues == result.get('mipvalue')
        assert test.variable_lookup == result.get('variable_lookup')
        assert test.enum_lookup == result.get('enum_lookups')
        assert recorded.list == []