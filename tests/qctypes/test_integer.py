from __future__ import division
from __future__ import print_function
from __future__ import absolute_import
from __future__ import unicode_literals

import pytest
import csv
from random import randint
from mipqctool.model import qctypes
from mipqctool.config import ERROR

# Tests


@pytest.mark.parametrize('value, result', [
    ('13', 'd'),
    ('13(cm3)', 'd(cm3)'),
    ('0.', ERROR),
    ('0.3 %', ERROR),
    ('23,4', ERROR),
    ('12341 123', ERROR),
    ('123.223 3', ERROR),
    ('test112', ERROR),
    ('1231 thisvery(long)suffix', ERROR),
    (14, 'd'),
    (32.32, ERROR),
    ('+31 (%)', 'd (%)'),
    ('231 12cm', ERROR),
    ('123 N/e', ERROR),
    ('31-40', ERROR)
])
def test_infer_integer(value, result):
    with pytest.warns(None) as recorded:
        assert qctypes.infer_integer(value) == result
        assert recorded.list == []


def create_uniques(size):
    """Creates a set of random integers."""
    sample = set([randint(0, 1000) for i in range(size)])
    while len(sample) != size:
        sample.add(randint(0, 1000))
    return sample


@pytest.mark.parametrize('pattern, uniques, result', [
    ('d %', create_uniques(15), {'type': 'integer',
                                 'format': 'default',
                                 'MIPType': 'integer',
                                 'bareNumber': False,
                                 'suffix': ' %'}),
    ('d.', create_uniques(3), ERROR),
    ('dcm3', create_uniques(4), {'type': 'integer',
                                 'format': 'default',
                                 'MIPType': 'integer',
                                 'bareNumber': False,
                                 'suffix': 'cm3'}),
    ('d', ['1', '2', '3', '4'], {'type': 'integer',
                                 'format': 'default',
                                 'MIPType': 'nominal',
                                 'constraints': {
                                     'enum': ['1', '2', '3', '4']
                                      },
                                 }),
    ('d', create_uniques(100), {'type': 'integer',
                                'format': 'default',
                                'MIPType': 'integer',
                                'bareNumber': True,
                                }),
    ('d m3', create_uniques(3), {'type': 'integer',
                                 'format': 'default',
                                 'MIPType': 'integer',
                                 'bareNumber': False,
                                 'suffix': ' m3'}),
    ('d', set(['0', '1']), {'type': 'boolean',
                            'format': 'default',
                            'MIPType': 'nominal',
                            'trueValues': ['1'],
                            'falseValues': ['0'],
                            }),
])
def test_describe_integer(pattern, uniques, result):
    with pytest.warns(None) as recorded:
        assert qctypes.describe_integer(pattern, uniques, 5) == result
        assert recorded.list == []


@pytest.mark.parametrize('pattern, result', [
    ('d div', ' div'),
    ('dcm3', 'cm3'),
    ('d long3sufix', ERROR)  # longer than 10 char
])
def test_get_suffix_integer(pattern, result):
    with pytest.warns(None) as recorded:
        assert qctypes.get_suffix_integer(pattern) == result
        assert recorded.list == []


@pytest.mark.parametrize('path, variable, result', [
    ('tests/test_datasets/integer.csv', 1,
     {'mode': 71, 'freq': 8,
      'min': 36, 'max': 87,
      'q1': 67, 'median': 71,
      'q3': 77}),
    ('tests/test_datasets/integer.csv', 2,
     {'mode': 0, 'freq': 86,
      'min': 0, 'max': 0,
      'q1': 0, 'median': 0,
      'q3': 0}),
    ('tests/test_datasets/integer.csv', 3,
     {'mode': 29, 'freq': 13,
      'min': 9, 'max': 30,
      'q1': 23, 'median': 26,
      'q3': 29}),
])
def test_profile_integer(path, variable, result):
    pairs = []
    field = 'Variable_%s' % variable
    with open(path, mode='r') as csv_file:
        csv_reader = csv.DictReader(csv_file)
        row_count = 1
        for row in csv_reader:
            try:
                pairs.append((row_count, int(row[field])))
            except ValueError:
                continue
            finally:
                row_count += 1
    with pytest.warns(None) as recorded:
        assert qctypes.profile_integer(pairs) == result
        assert recorded.list == []
