from __future__ import division
from __future__ import print_function
from __future__ import absolute_import
from __future__ import unicode_literals

import os
import pytest
from unittest.mock import Mock, PropertyMock, patch
from mipqctool.model.qcfrictionless.cde import CdeDict
from mipqctool.controller.columnreport import ColumnReport
from mipqctool.config import ERROR

DICT_PATH1 = 'tests/test_datasets/extract_mip_dictionary.xlsx'

VARIABLE_1 = ['gendreww', 'nominal', ['άνδρας', 'γυναίκα']]
VARIABLE_2 = ['handedness', 'nominal', None]
VARIABLE_3 = ['right aisantior insula', 'numerical', None]
VARIABLE_4 = ['verrryirrelevant', 'numerical', None]
VARIABLE_5 = ['gender', 'notexistingtype', None]
VARIABLE_6 = ['MADRS test', 'integer', [4, 44]]
VARIABLE_7 = ['MADRS testee', 'integer', [-12, 86]]
VARIABLE_8 = ['MADRS tewecew', 'integer', [44, 86]]
VARIABLE_9 = ['md nonsenese', 'integer', [-12, -2]]


@pytest.mark.parametrize('filename, result', [
    (DICT_PATH1, 168)
])
def test_total_cdes(filename, result):
    test = CdeDict(filename)
    assert test.total_cdes == result


@pytest.mark.parametrize('filename, variable, result', [
    (DICT_PATH1, VARIABLE_1, 'gender_type'),
    (DICT_PATH1, VARIABLE_2, 'hand'),
    (DICT_PATH1, VARIABLE_3, 'rightainsanteriorinsula'),
    (DICT_PATH1, VARIABLE_4,  None),
    (DICT_PATH1, VARIABLE_5,  None),
    (DICT_PATH1, VARIABLE_6, 'madrs'),
    (DICT_PATH1, VARIABLE_7, 'madrs'),
    (DICT_PATH1, VARIABLE_8, None),
    (DICT_PATH1, VARIABLE_9, None),
])
def test_suggest(filename, variable, result):
    test = CdeDict(filename)
    mockreport = Mock()
    type(mockreport).name = PropertyMock(return_value=variable[0])
    type(mockreport).miptype = PropertyMock(return_value=variable[1])
    type(mockreport).value_range = PropertyMock(return_value=variable[2])

    suggested_cde = test.suggest_cde(mockreport)
    if suggested_cde:
        totest = suggested_cde.code
    else:
        totest = None
    assert totest == result
