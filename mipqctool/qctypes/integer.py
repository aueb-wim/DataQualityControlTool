# -*- coding: utf-8 -*-
# numerical.py

from __future__ import division
from __future__ import print_function
from __future__ import absolute_import
from __future__ import unicode_literals

import re
import numpy as np
from collections import Counter, OrderedDict
from ..config import ERROR, LOGGER, DEFAULT_MISSING_VALUES
# Regex unicode support


def infer_integer(value, **options):
    """Find if the given string value it represents an integer.
    """
    result = None
    suffix = None
    strval = str(value)
    match = re.match(_INT, strval, flags=re.UNICODE)
    if match:
        result = 'd'
        if match.group('suffix'):
            suffix = match.group('suffix')
            result += suffix
    else:
        result = ERROR
    return result


def describe_integer(pattern, uniques, maxlevels=10):
    """Return a descriptor object based on given pattern.

    Arguments:
    :param pattern: string with qctype pattern
    :param uniques: set with unique values found
    :param maxlevels: threshold value for considering an integer
                      type value as nominal ie (0,1), (1,2,3,4)
    :return: dictionary descriptor
    """
    match = re.match(_PAT, pattern, flags=re.UNICODE)
    if match:
        if match.group('suffix'):
            return {
                'type': 'integer',
                'format': 'default',
                'MIPType': 'integer',
                'bareNumber': False,
                'suffix': match.group('suffix')
            }
        else:
            if uniques == set(['0', '1']):
                return {
                    'type': 'boolean',
                    'format': 'default',
                    'MIPType': 'nominal',
                    'trueValues': ['1'],
                    'falseValues': ['0'],
                }
            elif len(uniques) <= maxlevels:
                levels = list(uniques)
                levels.sort()
                return {
                    'type': 'integer',
                    'format': 'default',
                    'MIPType': 'nominal',
                    'constraints': {
                        'enum': levels
                    }
                }
            else:
                return {
                    'type': 'integer',
                    'format': 'default',
                    'MIPType': 'integer',
                    'bareNumber': True,
                }
    else:
        return ERROR


def get_suffix_integer(pattern):
    match = re.match(_PAT, pattern, flags=re.UNICODE)
    if match:
        if match.group('suffix'):
            return match.group('suffix')
    else:
        return ERROR


def profile_integer(pairs, **options):
    """Return stats for the integer field

    Arguments:
    :param pairs: list with pairs (row, value)
    :return: dictionary with stats
    """
    result = OrderedDict()
    # Get the values in an numpy array
    values = np.asarray([r[1] for r in pairs])
    c = Counter(values)
    result['mode'], result['freq'] = c.most_common(1)[0]
    result['min'] = np.min(values)
    result['max'] = np.max(values)
    # convert those stats to integer in case of zeros values
    result['q1'] = int(np.quantile(values, 0.25))
    result['median'] = int(np.median(values))
    result['q3'] = int(np.quantile(values, 0.75))

    return result


def suggestc_integer(value, **options):
    """Suggest a value for  the given value that violates the constraint.
    """
    null = options.get('missing_values', DEFAULT_MISSING_VALUES)[0]
    return null


def suggestd_integer(value, **options):
    """Suggest a value in the given datatype.
    """
    null = options.get('missing_values', DEFAULT_MISSING_VALUES)[0]
    try:
        # case value is float, try to round it
        suggested = str(int(float(value)))
    except ValueError:
        suggested = null

    return suggested

# Internal

_INT = (r'^(?P<sign>[+-])?\d+'
        r'(?P<suffix>(\s?[^0-9\s^&!*-+=~,\.`@\"\'\\\/]{1,10}\d{0,3})\)?)?$')

_PAT = (r'^[d]'
        r'(?P<suffix>(\s?[^0-9\s^&!*-+=~,\.`@\"\'\\\/]{1,10}\d{0,3})\)?)?$')
