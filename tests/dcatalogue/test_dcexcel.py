from __future__ import division
from __future__ import print_function
from __future__ import absolute_import
from __future__ import unicode_literals

import os
import pytest

from mipqctool.model.dcatalogue.dcexcel import DcExcel, ExcelVariable

DC_EXCEL_PATH = 'tests/test_datasets/invalid_dc_excel.xlsx'

@pytest.mark.parametrize('variable, result', [
    (['varialble1', 'nominal', '{"IN", "1.5t"}, {"2,4", "DC"}', '/root/var1'], {'IN', '1.5T', '2,4'}),
])
def test_invalid_nominal(variable, result):
    test = ExcelVariable(*variable)
    assert set(test.invalid_enums) == result


@pytest.mark.parametrize('filename, result', [
    (DC_EXCEL_PATH, set(['IN', '1.5T', '2,4']))
])
def test_invalid_enums(filename, result):
    test = DcExcel(filename)
    assert set(test.invalid_enums) == result