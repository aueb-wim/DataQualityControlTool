# test_qcpdutils.py
from __future__ import division
from __future__ import print_function
from __future__ import absolute_import
from __future__ import unicode_literals

import pandas as pd 
from mipqctool import qcpdutils

def test_dict4pandas():
    """Test for fucntion dict4pandas"""
    given = {'var1': ['value1'], 'var2': ['value2']}
    in_dict = {'var1': 'value1', 'var2': 'value2'}
    totest = qcpdutils.dict4pandas(in_dict)
    assert totest == given


def test_pandas2dict():
    """Test for function pandas2dict"""
    given = {'var1': 'value1', 'var2': 'value2'}
    in_dict = {'var1': ['value1', 'value12', 'value13'],
               'var2': ['value2', 'value22', 'value23']}
    in_df = pd.DataFrame(in_dict)
    totest = qcpdutils.pandas2dict(in_df)
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
    totest = qcpdutils.guess_nominal(initial_df, 3)
    assert given == totest