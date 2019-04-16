# -*- coding: utf-8 -*-
# numerical.py

from __future__ import division
from __future__ import print_function
from __future__ import absolute_import
from __future__ import unicode_literals

import re
import numpy as np
from ..config import ERROR, LOGGER


def infer_numerical(value, **options):
    """Find if the given string value it represents a number.
    """
    result = None
    decim_char = None
    suffix = None
    strval = str(value)
    match = re.match(_NUM, strval, flags=re.UNICODE)
    if match:
        # case of float number
        if match.group('decpart'):
            decim_char = match.group('decchar')
            result = 'd' + decim_char
        if match.group('suffix'):
            suffix = match.group('suffix')
            result += suffix
    else:
        result = ERROR
    return result


def describe_numerical(pattern, **options):
    """Return a descriptor object based on given pattern.

    Arguments:
    :param pattern: string with qctype pattern
    :return: dictionary descriptor
    """
    match = re.match(_PAT, pattern, flags=re.UNICODE)
    if match:
        if match.group('suffix'):
            return {'type': 'number',
                    'format': 'default',
                    'MIPType': 'numerical',
                    'decimalChar': match.group('decchar'),
                    'bareNumber': False,
                    'suffix': match.group('suffix')
                    }
        else:
            return {'type': 'number',
                    'format': 'default',
                    'MIPType': 'numerical',
                    'decimalChar': match.group('decchar'),
                    'bareNumber': True,
                    }
    else:
        return ERROR


def get_suffix_numerical(pattern):
    match = re.match(_PAT, pattern, flags=re.UNICODE)
    if match:
        if match.group('suffix'):
            return match.group('suffix')
    else:
        return ERROR


def profile_numerical(pairs):
    """Return stats for the numerical field

    Arguments:
    :param pairs: list with pairs (row, value)
    :return: dictionary with stats
    """
    result = {}
    # Get the values in an numpy array
    values = np.asarray([r[1] for r in pairs])

    result['mean'] = np.mean(values)
    # sample stadard deviation with 1 degree of freedom
    result['std'] = np.std(values, ddof=1)
    result['min'] = np.min(values)
    result['max'] = np.max(values)
    result['q1'] = np.quantile(values, 0.25)
    result['median'] = np.median(values)
    result['q3'] = np.quantile(values, 0.75)
    high = result['mean'] + 3 * result['std']
    result['upperbound'] = high
    low = result['mean'] - 3 * result['std']
    result['lowerbound'] = low
    result['outliersrows'] = list(filter(lambda x:
                                         x[1] >= high or x[1] <= low, pairs))
    result['outliers'] = len(result['outliersrows'])

    return result


# Internal

_NUM = (r'^(?P<sign>[+-])?\d+(?P<decpart>(?P<decchar>[,\.])\d*)'
        r'(?P<suffix>(\s?[^0-9\s^&!*-+=~,\.`@\"\'\\\/]{1,10}\d{0,3})\)?)?$')

_PAT = (r'^[d](?P<decchar>[.,])'
        r'(?P<suffix>(\s?[^0-9\s^&!*-+=~,\.`@\"\'\\\/]{1,10}\d{0,3})\)?)?$')
