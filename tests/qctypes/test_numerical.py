from __future__ import division
from __future__ import print_function
from __future__ import absolute_import
from __future__ import unicode_literals

import pytest
import csv
from copy import copy
from mipqctool.model import qctypes
from mipqctool.config import ERROR


# helper functions

def round_stats(stats, ndigits):
    """A fucntion for rounding statistical results"""
    new_stats = copy(stats)
    keys = ['mean', 'std', 'q1', 'q3', 'median',
            'upperbound', 'lowerbound']
    half = '0.' + (ndigits) * '0' + '5'
    half = float(half)
    for key in keys:
        new_stats[key] = round(stats[key], ndigits)

    return new_stats


# Tests


@pytest.mark.parametrize('value, result', [
    ('13', ERROR),
    ('13(cm3)', ERROR),
    ('0.', 'd.'),
    ('0.3 %', 'd. %'),
    ('23,4', 'd,'),
    ('12341 123', ERROR),
    ('123.223 3', ERROR),
    ('test112', ERROR),
    ('1231 thisvery(long)suffix', ERROR),
    (14, ERROR),
    (32.32, 'd.'),
    ('+31 (%)', ERROR),
])
def test_infer_numerical(value, result):
    with pytest.warns(None) as recorded:
        assert qctypes.infer_numerical(value) == result
        assert recorded.list == []


@pytest.mark.parametrize('pattern, result', [
    ('d.', {'type': 'number',
            'format': 'default',
            'MIPType': 'numerical',
            'decimalChar': '.',
            'bareNumber': True,
            }),
    ('d.cm3', {'type': 'number',
               'format': 'default',
               'MIPType': 'numerical',
               'decimalChar': '.',
               'bareNumber': False,
               'suffix': 'cm3'
               }),
    ('d cm3', ERROR),
])
def test_describe_numerical(pattern, result):
    with pytest.warns(None) as recorded:
        assert qctypes.describe_numerical(pattern) == result
        assert recorded.list == []


@pytest.mark.parametrize('pattern, result', [
    ('d. cm3', ' cm3'),
    ('d %', ERROR),
    ('d,', None),
    ('d.', None)
])
def test_get_suffix_numerical(pattern, result):
    with pytest.warns(None) as recorded:
        assert qctypes.get_suffix_numerical(pattern) == result
        assert recorded.list == []


@pytest.mark.parametrize('path, variable, result', [
    ('tests/test_datasets/random_numeric.csv', 1,
     {'mean': -0.0227587041, 'std': 0.9347881169,
      'min': -2.2315064208, 'max': 3.0881165577,
      'q1': -0.773279829, 'median': -0.0678199662,
      'q3': 0.610162354, 'upperbound': 2.7816056467,
      'lowerbound': -2.8271230549, 'outliers': 1,
      'outliersrows': [(93, 3.0881165577)]}),
    ('tests/test_datasets/random_numeric.csv', 3,
     {'mean': 3.6610246582, 'std': 2.6826183943,
      'min': 0.0189946653, 'max': 14.5695842802,
      'q1': 1.7913899685, 'median': 2.9051041444,
      'q3': 4.6617991592, 'upperbound': 11.7088798411,
      'lowerbound': -4.3868305247, 'outliers': 2,
      'outliersrows': [(49, 14.5695842802),
                       (93, 14.049638643)]})
])
def test_profile_numerical(path, variable, result):
    pairs = []
    field = 'Variable_%s' % variable
    with open(path, mode='r') as csv_file:
        row_count = 1
        csv_reader = csv.DictReader(csv_file)

        for row in csv_reader:
            pairs.append((row_count, float(row[field])))
            row_count += 1

    rounded = round_stats(qctypes.profile_numerical(pairs), 10)
    with pytest.warns(None) as recorded:
        assert rounded == result
        assert recorded.list == []
