# test_qcutils.py
import pandas as pd
from mipqctool import qcutils


def test_dict4pandas():
    """Test for fucntion dict4pandas"""
    given = {'var1': ['value1'], 'var2': ['value2']}
    in_dict = {'var1': 'value1', 'var2': 'value2'}
    totest = qcutils.dict4pandas(in_dict)
    assert totest == given


def test_pandas2dict():
    """Test for function pandas2dict"""
    given = {'var1': 'value1', 'var2': 'value2'}
    in_dict = {'var1': ['value1', 'value12', 'value13'],
               'var2': ['value2', 'value22', 'value23']}
    in_df = pd.DataFrame(in_dict)
    totest = qcutils.pandas2dict(in_df)
    assert totest == given


def test_guess_nominal():
    """Test the guess_nominal function"""
    given = ['nom1', 'nom2']
    initial_dict = {'str1': ['value1', 'value2', '21',
                             'value4', 'value5', '54'],
                    'nom1': ['val1', 'val2', 'val3',
                             'val1', 'val3', 'val3'],
                    'str2': ['val1', 'val2', 'val1',
                             'val3', 'val4', 'val1'],
                    'nom2': ['1', '1', '2',
                             '2', '1', '2']}
    initial_df = pd.DataFrame(initial_dict)
    totest = qcutils.guess_nominal(initial_df, 3)
    assert given == totest


def test_check_date():
    """Test the _check_date function"""
    inputdates = ['12/12/2001', '31.4.1995',
                  '32.3.2044', '55/12/22',
                  '31 Aug 1944', '5/25/44',
                  'Aug 31 2001', 'na', '21']
    given = ['date1', 'date1',
             'Not Date', 'date3',
             'date2', 'date5',
             'date4', 'Not Date', 'Not Date']
    totest = [qcutils.check_date(date)['datetype'] for date in inputdates]
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
        totest['dformat'] = len(counttypes['dateformats'])
        totest['datesep'] = len(counttypes['datesep'])
        totest['uniquestr'] = len(counttypes['stringvals'])
        assert given == totest


COMDATE1 = 'Warning! Dates with multiple formats.'
COMDATE2 = 'Warning! Dates with multiple seperators.'
COMDATE3 = 'Warning! Dates with only 2 digit year.'
COMMIX1 = 'Warning! Mixed type variable.'

def add_comment(comment, addcomments):
    finalcomment = comment
    for comment in addcomments:
        finalcomment = ' '.join([finalcomment, comment])
    return finalcomment

def test_add_date_comment():
    """Test for _add_date_comment function"""
    comments = [COMDATE1, COMDATE2, COMDATE3]
    given = add_comment('', comments)
    totest = qcutils._add_date_comments('', 2, 2, False)
    assert given == totest



class TestGuessType(object):
    """Tests for the guess_type function"""
    def give_com_na(self, nastring):
        return 'Possible NA value is <{0}>.'.format(nastring)

    def test_guess_date1(self):
        values = ['12/12/2001', 'NaN',
                  '21', '31 Aug 1995',
                  '31/11/55']
        comments = [COMMIX1, self.give_com_na('NaN'),
                    COMDATE1, COMDATE2,
                    COMDATE3]
        given_comment = add_comment('', comments)
        given_type = 'date'
        totest = qcutils.guess_type(values)
        assert (given_type, given_comment) == totest

    def test_guess_num1(self):
        values = ['22', 'INF', 'NAN', '33.2',
                  '12%', '111232']
        comments = [COMMIX1]
        given_comment = add_comment('', comments)
        totest = qcutils.guess_type(values)
        assert ('numerical', given_comment) == totest

    def test_guess_num2(self):
        values = [11, '22', 32.4, '321.311',
                  float('nan')]
        totest = qcutils.guess_type(values)
        assert ('numerical', '') == totest

    def test_guess_text1(self):
        values = ['nan', 'infinity', 'john',
                  'NAN', '100%', 'black',
                  float('nan')]
        given_comment = ''
        totest = qcutils.guess_type(values)
        assert ('text', given_comment) == totest
