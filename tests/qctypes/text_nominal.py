from __future__ import division
from __future__ import print_function
from __future__ import absolute_import
from __future__ import unicode_literals

import pytest
import csv
from mipqctool import qctypes
from mipqctool.config import ERROR

# Tests


@pytest.mark.parametrize('path, column, result', [
    ('data/nominal.csv', 1,
     {'top': 'NL', 'freq': 37,
      'categories': ['NL', 'AD', 'MCI'],
      'categories_num': 3}),
    ('data/nominal.csv', 2,
     {'top': '2', 'freq': 53,
      'categories': ['2', '1'],
      'categories_num': 2}),
])
def test_profile_nominal(path, column, result):
    pairs = []
    field = 'Variable_%s' % column
    with open(path, mode='r') as csv_file:
        csv_reader = csv.DictReader(csv_file)
        row_count = 1
        for row in csv_reader:
            pairs.append((row_count, row[field]))
    with pytest.warns(None) as recorded:
        assert qctypes.profile_nominal(pairs) == result
        assert recorded.list == []
