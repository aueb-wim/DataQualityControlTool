from __future__ import division
from __future__ import print_function
from __future__ import absolute_import
from __future__ import unicode_literals

import pytest
import os
import json
from mipqctool.tablereport import TableReport
from mipqctool.qctable import QcTable
from mipqctool.qcschema import QcSchema


APP_PATH = os.path.abspath(os.path.dirname(__file__))
DATASET1_PATH = os.path.join(APP_PATH, 'test_datasets/test_dataset.csv')
METADATA1_PATH = os.path.join(APP_PATH, 'test_datasets/test_dataset.json')
ID_STATS1 = {
    'rows_only_id': 1,
    'rows_no_id': 1
    }

FILLED_ROWS_STATS1 ={
    'filled_100': 14,
    'filled_75_99': 4,
    'filled_50_74': 1,
    'filled_25_49': 1,
    'filled_0_24': 0
    }

VALID_ROWS_STATS1 = {
    'valid_100': 11,
    'valid_75_99': 6,
    'valid_50_74': 2,
    'valid_25_49': 1,
    'valid_0_24': 0
    }

COR_FILLED_ROWS_STATS1 = {
    'filled_100': 8,
    'filled_75_99': 10,
    'filled_50_74': 1,
    'filled_25_49': 1,
    'filled_0_24': 0
}


F_ROWS_PER_COLUMN1 = {
   4: 14,
   3: 4,
   2: 1,
   1: 1
}


# these 3 lines is for creating the initial
# metadata json file with the dataset's schema
# TEST_TABLE = QcTable(DATASET1_PATH)
# TEST_TABLE.infer()
# TEST_TABLE.schema.save(os.path.join(APP_PATH, 'test_datasets/test_dataset.json')

@pytest.mark.parametrize('datasetpath, schemapath, id_column, result, total_rows', [
    (DATASET1_PATH, METADATA1_PATH, 'Patient_id', F_ROWS_PER_COLUMN1, 20)
])
def test_calc_rows_per_column(datasetpath, schemapath, id_column, result, total_rows):
    with open(schemapath) as json_file:
        dict_schema = json.load(json_file)
    schema = QcSchema(dict_schema)
    testtable = QcTable(datasetpath, schema=schema)
    testreport = TableReport(testtable, id_column)
    with pytest.warns(None) as recorded:
        assert testreport.total_rows == total_rows
        assert testreport._TableReport__tfilled_columns == result
        assert recorded.list == []





@pytest.mark.parametrize('datasetpath, schemapath, id_column, result', [
    (DATASET1_PATH, METADATA1_PATH, 'Patient_id', FILLED_ROWS_STATS1)
])
def test_filled_rows_stats(datasetpath, schemapath, id_column, result):
    with open(schemapath) as json_file:
        dict_schema = json.load(json_file)
    schema = QcSchema(dict_schema)
    testtable = QcTable(datasetpath, schema=schema)
    testreport = TableReport(testtable, id_column)
    with pytest.warns(None) as recorded:
        assert testreport.filled_rows_stats == result
        assert recorded.list == []

@pytest.mark.parametrize('datasetpath, schemapath, id_column, result', [
    (DATASET1_PATH, METADATA1_PATH, 'Patient_id', VALID_ROWS_STATS1)
])
def test_valid_rows_stats(datasetpath, schemapath, id_column, result):
    with open(schemapath) as json_file:
        dict_schema = json.load(json_file)
    schema = QcSchema(dict_schema)
    testtable = QcTable(datasetpath, schema=schema)
    testreport = TableReport(testtable, id_column)
    with pytest.warns(None) as recorded:
        assert testreport.valid_rows_stats == result
        assert recorded.list == []


@pytest.mark.parametrize('datasetpath, schemapath, id_column, result', [
    (DATASET1_PATH, METADATA1_PATH, 'Patient_id', COR_FILLED_ROWS_STATS1)
])
def test_corrected_filled_rows_stats(datasetpath, schemapath, id_column, result):
    with open(schemapath) as json_file:
        dict_schema = json.load(json_file)
    schema = QcSchema(dict_schema)
    testtable = QcTable(datasetpath, schema=schema)
    testreport = TableReport(testtable, id_column)
    testreport.printpdf(os.path.join(APP_PATH, 'test_datasets/dataset_report.pdf'))
    testreport.apply_corrections()
    testreport.printpdf(os.path.join(APP_PATH, 'test_datasets/dataset_report_after.pdf'))
    testreport.save_corrected(os.path.join(APP_PATH, 'test_datasets/corrected.csv'))
    with pytest.warns(None) as recorded:
        assert testreport.filled_rows_stats == result
        assert recorded.list == []
