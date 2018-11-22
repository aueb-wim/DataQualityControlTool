# qcutils.py

import pandas as pd


def outliers(numbers, times):
    """Returns the number of outliers of a given list of numbers.
    As outliers are considered the values that outside the    
    space (mean - times * std, mean + times * std).
    
    Arguments:
    :param numbers: array or pandas Series
    :param times: number
    :return: an integer
    """
    assert isinstance(numbers, pd.core.series.Series), 'numbers must be panda Series'
    assert isinstance(times, (int, float)), 'times must be a number'
    mean, std = numbers.mean(), numbers.std()
    # Define upper bound of the space of non-outliers
    upper = mean + times * std
    # Define the lower bound of the space of non-outliers
    lower = mean - times * std
    # Return how many values are not inside this space
    return len(numbers[(numbers < lower) | (numbers > upper)])


def dict4pandas(d):
    """Takes a dict {key : value} and returns dict {key : [value]}"""
    new_dict = {}
    for key in d.keys():
        new_dict[key] = [d[key]]
    return new_dict

def pandas2dict(df):
    """Takes a pd Dataframe and returns
    a dict {column : value} of the first row only"""
    new_dict = df.to_dict(orient='records')
    return new_dict[0]
