from __future__ import division
from __future__ import print_function
from __future__ import absolute_import
from __future__ import unicode_literals

import pytest
import csv
from mipqctool import qctypes
from mipqctool.config import ERROR, DEFAULT_MISSING_VALUES

NULL = DEFAULT_MISSING_VALUES[0]

# Tests


@pytest.mark.parametrize('path, column, result', [
    ('data/nominal.csv', 1,
     {'top': 'NL', 'freq': 37,
      'categories': set(['AD', 'MCI', 'NL']),
      'categories_num': 3}),
    ('data/nominal.csv', 2,
     {'top': '2', 'freq': 53,
      'categories': set(['2', '1']),
      'categories_num': 2}),
])
def test_profile_nominal(path, column, result):
    pairs = []
    field = 'Variable_%s' % column
    with open(path, mode='r') as csv_file:
        csv_reader = csv.DictReader(csv_file)
        row_count = 1
        for row in csv_reader:
            # remove emty strings
            if row[field] != '':
                pairs.append((row_count, row[field]))
        profile = qctypes.profile_nominal(pairs)
        profile['categories'] = set(profile['categories'])
    with pytest.warns(None) as recorded:
        assert profile == result
        assert recorded.list == []


@pytest.mark.parametrize('value, enum, result', [
    ('famele', ['Female', 'Male'], 'Female'),
    ('AL', ['AD', 'DL', 'DA'], 'AD'),
    ('scleropssis', ['sclerosis', 'parkinson', 'demensia'], 'sclerosis'),
    ('Cat', ['Cat1', 'Cat2', 'Cat3'], 'Cat1'),
    ('CATEGORY1', ['category1', 'category2', 'category3'], 'category1'),
    ('31', ['1', '2', '3'], '1'),
    ('13', ['1', '2', '3'], '1'),
    ('NARWR', ['helo', 'dussan', 'lampda'], NULL)
])
def test_suggestc_nominal(value, enum, result):
    with pytest.warns(None) as recorded:
        assert qctypes.suggestc_nominal(value, enum=enum) == result
        assert recorded.list == []
