from __future__ import division
from __future__ import print_function
from __future__ import absolute_import
from __future__ import unicode_literals

import pytest

from mipqctool.model.mapping.csvdb import CsvDB
from mipqctool.config import ERROR

TEST_CSV_PATH1 = 'tests/test_datasets/nominal.csv'
TEST_CSV_PATH2 = 'tests/test_datasets/simple.csv'

FILE_LIST = [TEST_CSV_PATH1, TEST_CSV_PATH2]

TEST_CSV_HEADERS1 = ['Patient_id', 'Variable_1', 'Variable_2']


@pytest.mark.parametrize('filepaths, result', [
    (FILE_LIST, 2)
])
def test_totaltables(filepaths, result):
    test = CsvDB('csv_test_db', filepaths)
    assert test.name == 'csv_test_db'
    assert test.dbtype == 'CSV'
    assert test.totaltables == result




@pytest.mark.parametrize('filepaths, filename,  result', [
    (FILE_LIST, 'nominal.csv', TEST_CSV_HEADERS1),
    (FILE_LIST, 'nonexisting.csv', None)
])
def test_table_headers(filepaths, filename,  result):
    test = CsvDB('csv_test_db', filepaths)
    assert test.get_table_headers(filename) == result

@pytest.mark.parametrize('filepaths, filename, column, dublication, result', [
    (FILE_LIST, 'nominal.csv', 'Patient_id', None, 'csv_test_db.nominal.nominalTuple.Patient_id'),
    (FILE_LIST, 'nominal.csv', 'Patient_id', 1, 'csv_test_db.nominal_1_.nominalTuple.Patient_id')
])
def test_columnforxml(filepaths, filename, column, dublication, result):
    test = CsvDB('csv_test_db', filepaths)
    assert test.columnforxml(filename, column, dublication=dublication) == result
