# test_qcutils.py

from __future__ import division
from __future__ import print_function
from __future__ import absolute_import
from __future__ import unicode_literals

import pandas as pd
from mipqctool import qcutils
from mipqctool.qcutils import COMDATE1, COMDATE2, COMDATE3
from mipqctool.qcutils import COMNUM_DEC, COMNUM_MIXED, COMNUM_SUFIXES, COMMIX1


def test_check_date():
    """Test the check_date function"""
    inputdates = ['12/12/2001', '31.4.1995',
                  '32.3.2044', '55/12/22',
                  '31 Aug 1944', '5/25/44',
                  'Aug 31 2001', 'na', '21',
                  221295, 2001911, 3151995]
    given = ['date1', 'date1',
             'Not Date', 'date3',
             'date4', 'date2',
             'date6', 'Not Date', 'Not Date',
             'Not Date', 'date10', 'date8']
    totest = [qcutils.check_date(date)['datetype'] for date in inputdates]
    assert given == totest


def test_check_num():
    """Test to check check_num function."""
    numstrs = ['2.123', '54 cm3',
               '+23.23(%)', 'INF',
               'NaN', '']
    given_types = ['number', 'number',
                   'number', 'Not Number',
                   'na_type', 'na_type']
    given_sufixes = [None, ' cm3',
                     '(%)', None,
                     None, None]
    given_navalues = [None, None,
                      None, None,
                      'NaN', '']
    given_decsep = ['.', None,
                    '.', None,
                    None, None]
    totest = [(qcutils.check_num(num)['numtype'],
               qcutils.check_num(num)['sufix'],
               qcutils.check_num(num)['nanvalue'],
               qcutils.check_num(num)['decimalchar'])
              for num in numstrs]
    given = list(zip(given_types, given_sufixes, 
                     given_navalues, given_decsep))
    assert given == totest


class TestCountTypes(object):
    """Tests for the _count_types function"""
    def test_count_uniques(self):
        values = ['na', 'na', 'naN',
                  '12/12/2001', '12.12.2044',
                  '31 Aug 2004', '21']
        given = {'numerical': 1,
                 'date': 3,
                 'text': 3,
                 'dformat': 2,
                 'datesep': 3,
                 'fullyear': True,
                 'uniquestr': 2}

        keys = ['numerical', 'date', 'text', 'fullyear']
        counttypes = qcutils._count_types(values)
        totest = {k: counttypes[k] for k in keys}
        totest['dformat'] = len(counttypes['datetypes'])
        totest['datesep'] = len(counttypes['dateseps'])
        totest['uniquestr'] = len(counttypes['vocabulary'])
        assert given == totest


def add_comment(comment, addcomments):
    finalcomment = comment
    for comm in addcomments:
        finalcomment = ' '.join([finalcomment, comm])
    return finalcomment


def test_add_date_comment():
    """Test for _add_date_comment function"""
    comments = [COMDATE1, COMDATE2, COMDATE3]
    given = add_comment('', comments)
    totest = qcutils._add_date_comments('', 2, 2, False)
    assert given == totest


def test_add_num_comment():
    """Test for _add_date_comment function"""
    sufixes = ['cm3', 'meter']
    comments = [COMNUM_MIXED, COMNUM_SUFIXES]
    given = add_comment('', comments)    
    totest = qcutils._add_num_comments('', 1, True, sufixes)
    assert given == totest


class TestGuessType(object):
    """Tests for the guess_type function"""
    def test_guess_date1(self):
        values = ['12/12/55', 'NaN',
                  '21', '31 Aug 1995',
                  '31/11/2001']
        comments = [COMDATE1, COMDATE2,
                    COMDATE3, COMMIX1,
                    qcutils._give_com_na(['NaN'])]
        given_comment = add_comment('', comments)
        given_type = 'date'
        totest = qcutils.guess_type(values)
        assert (given_type, given_comment) == totest

    def test_guess_num1(self):
        values = ['22', 'INF', 'NAN', '33.2',
                  '12%', '111232', 'NaN']
        strings = ['INF', 'NAN']
        nans = ['NaN']
        comments = [COMMIX1,
                    qcutils._give_com_na(nans),
                    qcutils._give_com_na(strings, possible=True)]
        given_comment = add_comment('', comments)
        totest = qcutils.guess_type(values)
        assert ('numerical', given_comment) == totest

    def test_guess_num2(self):
        values = ['11', '22', '32.4', '321.311',
                  'nan', '']
        nans = ['nan', '']
        comments = [qcutils._give_com_na(nans)]
        given_comment = add_comment('', comments)
        totest = qcutils.guess_type(values)
        assert ('numerical', given_comment) == totest

    def test_guess_text1(self):
        values = ['nan', 'infinity', 'john',
                  'NAN', '100SFD%321', 'black',
                  'nan']
        nans = ['nan']
        comments = [qcutils._give_com_na(nans)]
        given_comment = add_comment('', comments)
        totest = qcutils.guess_type(values)
        assert ('text', given_comment) == totest
