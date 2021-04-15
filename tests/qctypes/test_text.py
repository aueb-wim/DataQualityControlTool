from __future__ import division
from __future__ import print_function
from __future__ import absolute_import
from __future__ import unicode_literals

import os
import pytest
import csv
from pathlib import Path

from mipqctool.model import qctypes
from mipqctool.config import ERROR

# Tests
TESTS_BASE_DIR = Path(__file__).resolve().parent.parent

TEST_TEXT_PATH = os.path.join(str(TESTS_BASE_DIR), 'test_datasets', 'text.csv')

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
    (TEST_TEXT_PATH, 1,
     {'top': 'Germany', 'freq': 17, 'unique': 13, 
      'top5': ['Germany', 'Italy', 'Netherlands', 'Denmark', 'Belgium'],
      'bottom5': ['Austria', 'Albania', 'Ireland', 'Turkey', 'Spain']}),
    (TEST_TEXT_PATH, 2,
     {'top': '', 'freq': 100, 'unique': 1,
      'top5': [''], 'bottom5': ['']})
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
