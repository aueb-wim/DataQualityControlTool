from __future__ import division
from __future__ import print_function
from __future__ import absolute_import
from __future__ import unicode_literals

import pytest
import csv
from datetime import datetime, date
from mipqctool import qctypes
from mipqctool.config import ERROR

# Tests


@pytest.mark.parametrize('value, result', [
    ('31/5/1980', '%d/%m/%Y'),
    ('23-06-2017', '%d-%m-%Y'),
    ('12.15.2017', '%m.%d.%Y'),
    ('2019-01-01', '%Y-%m-%d'),
    ('31-Aug-1955', '%d-%b-%Y'),
    ('12 June 1985', '%d %B %Y'),
    ('Aug-31-1944', '%b-%d-%Y'),
    ('August 31 1955', '%B %d %Y'),
    ('Aug/31/1955', ERROR),
    ('14 Αυγούστου 1976', '%d %B %Y'),
    ('Αύγουστος 13 1980', '%B %d %Y'),
])
def test_infer_date(value, result):
    with pytest.warns(None) as recorded:
        assert qctypes.infer_date(value) == result
        assert recorded.list == []


@pytest.mark.parametrize('pattern, result', [
    ('%d-%m-%Y', {'type': 'date',
                  'format': '%d-%m-%Y',
                  'MIPType': 'date'
                  }),
    ('%d/%m-%Y', ERROR),
])
def test_describe_date(pattern, result):
    with pytest.warns(None) as recorded:
        assert qctypes.describe_date(pattern) == result
        assert recorded.list == []


@pytest.mark.parametrize('path, variable, format, result', [
    ('data/dates.csv', 1, '%Y-%m-%d',
     {'mode': date(2001, 5, 31), 'freq': 6,
      'min': date(2001, 5, 31),
      'max': date(2001, 6, 26)}),
    ('data/dates.csv', 2, '%d/%m/%Y',
     {'mode': date(2011, 6, 16), 'freq': 2,
      'min': date(1936, 6, 4),
      'max': date(2019, 5, 31)}),
])
def test_profile_date(path, variable, format, result):
    pairs = []
    field = 'Variable_%s' % variable
    with open(path, mode='r') as csv_file:
        csv_reader = csv.DictReader(csv_file)
        row_count = 1
        for row in csv_reader:
            try:
                dateval = datetime.strptime(row[field], format).date()
                pairs.append((row_count, dateval))
            except ValueError:
                continue
            finally:
                row_count += 1
    with pytest.warns(None) as recorded:
        assert qctypes.profile_date(pairs) == result
        assert recorded.list == []


@pytest.mark.parametrize('value, result', [
    ('23-06-2017', '23/06/2017'),
    ('12.15.2017', '15/12/2017'),
    ('2019-01-01', '01/01/2019'),
    ('31-Aug-1955', '31/08/1955'),
    ('12 June 1985', '12/06/1985'),
    ('Aug-31-1944', '31/08/1944'),
    ('August 31 1955', '31/08/1955'),
    ('Aug/31/1955', None),
    ('notadate', None)
])
def test_suggestd_date(value, result):
    with pytest.warns(None) as recorded:
        if result:
            result = datetime.strptime(result, '%d/%m/%Y').date()
        assert qctypes.suggestd_date(value) == result
        assert recorded.list == []
