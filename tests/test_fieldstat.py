from __future__ import division
from __future__ import print_function
from __future__ import absolute_import
from __future__ import unicode_literals

import pytest
import csv
from mipqctool.fieldstat import FieldStat


# Tests

@pytest.mark.parametrize('desc, valid, invalid, na, result', [
    ({'MIPType': 'nominal'},
     [(0, 'ad'), (1, 'ad'), (2, 'bc'), (3, 'ab')],
     [(4, '23'), (5, '12/15/2001'), (9, '34')],
     [(6, 'nan'), (7, 'NaN'), (8, '')],
     {'valid': 4, 'invalid': 3, 'na': 3,
      'total_rows': 10, 'valid%': 40.00, 'invalid%': 30.00,
      'na%': 30.00, 'top': 'ad', 'freq': 2, 'categories_num': 3,
      'categories': ['ab', 'ad', 'bc']}),
    ({'MIPType': 'integer'},
     [(0, 1), (1, 1), (2, 1), (3, 2), (4, 5), (5, 6), (6, 6),
      (7, 6), (8, 6), (8, 6)], None, None,
      {'valid': 10, 'invalid': 0, 'na': 0,
       'total_rows': 10, 'valid%': 100.00, 'invalid%': 0.00,
       'na%': 0.00, 'mode': 6, 'freq': 5, 'min': 1, 'max': 6,
       'q1': 1, 'median': 5, 'q3': 6}),
    ({'MIPType': 'integer'}, None, None,
     [(0, 'NA'), (1, 'NA'), (2, '')],
     {'valid': 0, 'invalid': 0, 'na': 3, 'total_rows': 3,
      'valid%': 0.00, 'invalid%': 0.00, 'na%': 100.00}),
])
def test_fieldstat_nominal(desc, valid, invalid, na, result):
    fieldstat = FieldStat(desc)
    with pytest.warns(None) as recorded:
        assert fieldstat.get(valid, invalid, na) == result
        assert recorded.list == []
