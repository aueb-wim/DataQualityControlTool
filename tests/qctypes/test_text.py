from __future__ import division
from __future__ import print_function
from __future__ import absolute_import
from __future__ import unicode_literals

import pytest
import csv
from mipqctool import qctypes
from mipqctool.config import ERROR

# Tests


@pytest.mark.parametrize('value, result', [
    ('NaN', 'nan'),
    ('NAN', 'text'),
    ('NA', 'nan'),
    ('43', 'text'),
    ('34.34', 'text'),
    (43, ERROR),
])
def test_infer_text(value, result):
    with pytest.warns(None) as recorded:
        assert qctypes.infer_text(value) == result
        assert recorded.list == []


@pytest.mark.parametrize('pattern, uniques, result', [
    ('text', set(['t', 'e', 's', 'd']), {'type': 'string',
                                         'format': 'default',
                                         'MIPType': 'text'
                                         }),
    ('text', ['t', 'y', 'd'], {'type': 'string',
                               'format': 'default',
                               'MIPType': 'nominal',
                               'constraints': {
                                   'enum': ['d', 't', 'y']
                               }
                               }),
    ('nan', [''], ERROR),
])
def test_describe_text(pattern, uniques, result):
    with pytest.warns(None) as recorded:
        assert qctypes.describe_text(pattern, uniques, 3) == result
        assert recorded.list == []


@pytest.mark.parametrize('path, column, result', [
    ('data/text.csv', 1,
     {'top': 'Germany', 'freq': 17,
      'top5': ['Germany', 'Italy', 'Netherlands', 'Denmark', 'Belgium'],
      'bottom5': ['Austria', 'Albania', 'Ireland', 'Turkey', 'Spain']}),
])
def test_profile_text(path, column, result):
    pairs = []
    field = 'Variable_%s' % column
    with open(path, mode='r') as csv_file:
        csv_reader = csv.DictReader(csv_file)
        row_count = 1
        for row in csv_reader:
            pairs.append((row_count, row[field]))
    with pytest.warns(None) as recorded:
        assert qctypes.profile_text(pairs) == result
        assert recorded.list == []
