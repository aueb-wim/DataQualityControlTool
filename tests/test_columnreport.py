from __future__ import division
from __future__ import print_function
from __future__ import absolute_import
from __future__ import unicode_literals

import pytest
import os
from mipqctool.columnreport import ColumnReport
from mipqctool.qcfrictionless import QcField
from mipqctool.config import ERROR


MISSING_VALUES = ['']
DATE_DESC = {'name': 'testvar',
             'format': '%d/%m/%Y',
             'type': 'date',
             'MIPType': 'date',
             'constraints': {
                    'minimum': '1/1/1900',
                    }
             }
NOMINAL_DESC = {'name': 'testvar',
                'format': 'default',
                'type': 'string',
                'MIPType': 'nominal',
                'constraints': {
                    'enum': ['Category1', 'Category2', 'Another3']
                }}
NUMERICAL_DESC = {'name': 'testvar',
                  'format': 'default',
                  'type': 'number',
                  'MIPType': 'numerical',
                  'constraints': {
                      'minimum': 0,
                      'maximum': 10
                      }
                  }
INTEGER_DESC = {'name': 'testvar',
                'format': 'default',
                'type': 'integer',
                'MIPType': 'integer',
                'constraints': {
                    'minimum': 3,
                    'maximum': 5
                    }
                }

INTEGER_VALUES = ['1', '3', '3', '2', '5', '4', '2.5', '',
                  'not_int', '20191212', '5.6']
NUMERICAL_VALUES = ['-0.12', '2.31', 'not_num', '21/12/2019',
                    '4', '3.2', '', '']
DATE_VALUES = ['1/12/2019', '1-21-2013', '15 Aug 2012', '20011212', '',
               '31', 'not_date', '1/1/1880']
NOMINAL_VALUES = ['cAtegory1', 'not_value', 'Category1', 'Category2',
                  'anoter1', '', '', 'Category2', 'CATEGOR2']

@pytest.mark.parametrize('descriptor, values, result', [
    (INTEGER_DESC, INTEGER_VALUES, [8]),
    (NUMERICAL_DESC, NUMERICAL_VALUES, [7, 8]),
    (DATE_DESC, DATE_VALUES, [5]),
    (NOMINAL_DESC, NOMINAL_VALUES, [6, 7])
])
def test_null_rows(descriptor, values, result):
    testfield = QcField(descriptor)
    testcolumn = ColumnReport(values, testfield)
    testcolumn.validate()
    with pytest.warns(None) as recorded:
        assert testcolumn.null_row_numbers == set(result)
        assert recorded.list == []


@pytest.mark.parametrize('descriptor, values, result', [
    (INTEGER_DESC, INTEGER_VALUES, [1, 4, 7, 9, 10, 11]),
])
def test_violated_rows(descriptor, values, result):
    testfield = QcField(descriptor)
    testcolumn = ColumnReport(values, testfield)
    testcolumn.validate()
    with pytest.warns(None) as recorded:
        assert testcolumn.invalid_rows == set(result)
        assert recorded.list == []

@pytest.mark.parametrize('descriptor, values, result', [
    (INTEGER_DESC, INTEGER_VALUES,
     [(2, '3'), (3, '3'), (5, '5'), (6, '4'), (8, '')]),
    (NUMERICAL_DESC, NUMERICAL_VALUES,
     [(2, '2.31'), (5, '4'), (6, '3.2'), (7, ''), (8, '')]),
    (DATE_DESC, DATE_VALUES, [(1, '1/12/2019'), (5, '')]),
    (NOMINAL_DESC, NOMINAL_VALUES,
     [(3, 'Category1'), (4, 'Category2'), (6, ''), (7, ''),
      (8, 'Category2')])
])
def test_validate_valid(descriptor, values, result):
    testfield = QcField(descriptor)
    testcolumn = ColumnReport(values, testfield)
    testcolumn.validate()
    with pytest.warns(None) as recorded:
        assert testcolumn._ColumnReport__validated_pairs == result
        assert recorded.list == []


@pytest.mark.parametrize('descriptor, values, result', [
    (INTEGER_DESC, INTEGER_VALUES, [(7, '2.5'), (9, 'not_int'), (11, '5.6')]),
    (NUMERICAL_DESC, NUMERICAL_VALUES,
     [(3, 'not_num'), (4, '21/12/2019')]),
    (DATE_DESC, DATE_VALUES,
     [(2, '1-21-2013'), (3, '15 Aug 2012'), (4, '20011212'),
      (6, '31'), (7, 'not_date')]),
    (NOMINAL_DESC, NOMINAL_VALUES, [])
])
def test_validate_datatype(descriptor, values, result):
    testfield = QcField(descriptor)
    testcolumn = ColumnReport(values, testfield)
    testcolumn.validate()
    with pytest.warns(None) as recorded:
        assert testcolumn._ColumnReport__datatype_violated_pairs == result
        assert recorded.list == []


@pytest.mark.parametrize('descriptor, values, result', [
    (INTEGER_DESC, INTEGER_VALUES, [(1, '1'), (4, '2'), (10, '20191212')]),
    (NUMERICAL_DESC, NUMERICAL_VALUES, [(1, '-0.12')]),
    (DATE_DESC, DATE_VALUES, [(8, '1/1/1880')]),
    (NOMINAL_DESC, NOMINAL_VALUES, [(1, 'cAtegory1'), (2, 'not_value'),
                                    (5, 'anoter1'), (9, 'CATEGOR2')])
])
def test_validate_contraint(descriptor, values, result):
    testfield = QcField(descriptor)
    testcolumn = ColumnReport(values, testfield)
    testcolumn.validate()
    with pytest.warns(None) as recorded:
        assert testcolumn._ColumnReport__constraint_violated_pairs == result
        assert recorded.list == []


@pytest.mark.parametrize('descriptor, values, result', [
    (INTEGER_DESC, INTEGER_VALUES, ['', '', '5']),
    (NUMERICAL_DESC, NUMERICAL_VALUES, ['', '']),
    (DATE_DESC, DATE_VALUES, ['21/01/2013', '15/08/2012', '12/12/2001', '', '']),
    (NOMINAL_DESC, NOMINAL_VALUES, [])
 ])
def test_suggestions_d(descriptor, values, result):
    testfield = QcField(descriptor)
    testcolumn = ColumnReport(values, testfield)
    testcolumn.validate()
    totest = [sugestion.newvalue
              for sugestion in testcolumn._ColumnReport__dsuggestions]
    with pytest.warns(None) as recorded:
        assert totest == result
        assert recorded.list == []


@pytest.mark.parametrize('descriptor, values, result', [
    (INTEGER_DESC, INTEGER_VALUES, ['', '', '']),
    (NUMERICAL_DESC, NUMERICAL_VALUES, ['']),
    (DATE_DESC, DATE_VALUES, ['']),
    (NOMINAL_DESC, NOMINAL_VALUES, ['Category1', '', 'Another3',
                                    'Category2'])
 ])
def test_suggestions_c(descriptor, values, result):
    testfield = QcField(descriptor)
    testcolumn = ColumnReport(values, testfield)
    testcolumn.validate()
    totest = [sugestion.newvalue
              for sugestion in testcolumn._ColumnReport__csuggestions]
    with pytest.warns(None) as recorded:
        assert totest == result
        assert recorded.list == []


@pytest.mark.parametrize('descriptor, values, result', [
    (INTEGER_DESC, INTEGER_VALUES, [4, 1]),
    (NUMERICAL_DESC, NUMERICAL_VALUES, [3, 2]),
    (DATE_DESC, DATE_VALUES, [1, 1]),
    (NOMINAL_DESC, NOMINAL_VALUES, [3, 2])
])
def test_calc_nulls_nocorrection(descriptor, values, result):
    testfield = QcField(descriptor)
    testcolumn = ColumnReport(values, testfield)
    testcolumn.validate()
    totest = []
    totest.append(testcolumn.not_nulls_total)
    totest.append(testcolumn.nulls_total)
    with pytest.warns(None) as recorded:
        assert totest == result
        assert recorded.list == []


@pytest.mark.parametrize('descriptor, values, result', [
    (INTEGER_DESC, INTEGER_VALUES, [5, 6]),
    (NUMERICAL_DESC, NUMERICAL_VALUES, [3, 5]),
    (DATE_DESC, DATE_VALUES, [4, 4]),
    (NOMINAL_DESC, NOMINAL_VALUES, [6, 3])
])
def test_calc_nulls_withcorrection(descriptor, values, result):
    testfield = QcField(descriptor)
    testcolumn = ColumnReport(values, testfield)
    testcolumn.validate()
    testcolumn.apply_corrections()
    totest = []
    totest.append(testcolumn.not_nulls_total)
    totest.append(testcolumn.nulls_total)
    with pytest.warns(None) as recorded:
        assert totest == result
        assert recorded.list == []


@pytest.mark.parametrize('descriptor, values, result', [
    (INTEGER_DESC, INTEGER_VALUES,
     ['', '3', '3', '', '5', '4', '', '',
      '', '', '5']),
    (NUMERICAL_DESC, NUMERICAL_VALUES,
     ['', '2.31', '', '',
      '4', '3.2', '', '']),
    (DATE_DESC, DATE_VALUES,
     ['1/12/2019', '21/01/2013', '15/08/2012', '12/12/2001', '',
      '', '', '']),
    (NOMINAL_DESC, NOMINAL_VALUES,
     ['Category1', '', 'Category1', 'Category2',
      'Another3', '', '', 'Category2', 'Category2'])
])
def test_corrected_values(descriptor, values, result):
    testfield = QcField(descriptor)
    testcolumn = ColumnReport(values, testfield)
    testcolumn.validate()
    testcolumn.apply_corrections()
    with pytest.warns(None) as recorded:
        assert testcolumn.corrected_values == result
        assert recorded.list == []


@pytest.mark.parametrize('descriptor, values, resnulls, rescorr', [
    (INTEGER_DESC, INTEGER_VALUES,
     set(['2.5', 'not_int']), set([('5.6', '5')])),
    (NUMERICAL_DESC, NUMERICAL_VALUES,
     set(['not_num', '21/12/2019']), set()),
    (DATE_DESC, DATE_VALUES,
     set(['31', 'not_date']),
     set([('1-21-2013', '21/01/2013'),
          ('15 Aug 2012', '15/08/2012'),
          ('20011212', '12/12/2001')]))
])
def test_dnulls(descriptor, values, resnulls, rescorr):
    testfield = QcField(descriptor)
    testcolumn = ColumnReport(values, testfield)
    testcolumn.validate()
    with pytest.warns(None) as recorded:
        assert testcolumn.dnulls == resnulls
        assert testcolumn.dcorrections == rescorr
        assert recorded.list == []


@pytest.mark.parametrize('descriptor, values, resnulls, rescorr, path', [
    (INTEGER_DESC, INTEGER_VALUES,
     set(['1', '2', '20191212']), set(), 'test_datasets/int_report.pdf'),
    (NUMERICAL_DESC, NUMERICAL_VALUES,
     set(['-0.12']), set(), 'test_datasets/num_report.pdf'),
    (NOMINAL_DESC, NOMINAL_VALUES,
     set(['not_value']),
     set([('cAtegory1', 'Category1'),
          ('anoter1', 'Another3'),
          ('CATEGOR2', 'Category2')]), 'test_datasets/nom_report.pdf')

])
def test_cnulls(descriptor, values, resnulls, rescorr, path):
    app_path = os.path.abspath(os.path.dirname(__file__))
    report_path = os.path.join(app_path, path)
    testfield = QcField(descriptor)
    testcolumn = ColumnReport(values, testfield)
    testcolumn.validate()
    testcolumn.printpdf(report_path)
    with pytest.warns(None) as recorded:
        assert testcolumn.cnulls == resnulls
        assert testcolumn.ccorrections == rescorr
        assert recorded.list == []
