# -*- coding: utf-8 -*-
# text.py

from __future__ import division
from __future__ import print_function
from __future__ import absolute_import
from __future__ import unicode_literals

import re
from collections import Counter, OrderedDict
from mipqctool.config import ERROR, LOGGER, PANDAS_NANS, DEFAULT_MISSING_VALUES


def infer_text(value, **options):
    """Find if the given string value it represents a date or NaN.
    """
    na_empty_strings_only=options.get('na_empty_strings_only')
    if na_empty_strings_only:
        missing_values = DEFAULT_MISSING_VALUES
    else:
        missing_values = PANDAS_NANS
    if isinstance(value, str):
        if value in missing_values:
            return 'nan'
        else:
            return 'text'
    else:
        return ERROR


def describe_text(pattern, uniques, maxlevels=10):
    """Return a descriptor object based on given pattern.

    Arguments:
    :param pattern: string with qctype pattern
    :param uniques: set with unique values found
    :param maxlevels: threshold value for considering an integer
                      type value as nominal ie (0,1), (1,2,3,4)
    :return: dictionary descriptor
    """
    if pattern == 'text' and len(uniques) <= maxlevels:
        levels = list(uniques)
        levels.sort()
        return {
            'type': 'string',
            'format': 'default',
            'MIPType': 'nominal',
            'constraints': {
                'enum': levels
            }
        }
    elif pattern == 'text' and len(uniques) > maxlevels:
        return {
            'type': 'string',
            'format': 'default',
            'MIPType': 'text'
        }
    else:
        return ERROR


def profile_text(pairs, **options):
    """Return stats for the text field

    Arguments:
    :param pairs: list with pairs (row, value)
    :return: dictionary with stats
    """
    result = OrderedDict()
    # Get the values in an numpy array
    values = [r[1] for r in pairs]
    c = Counter(values)
    result['unique'] = len(list(c))
    result['top'], result['freq'] = c.most_common(1)[0]
    result['top5'] = [count[0] for count in c.most_common(5)]
    result['bottom5'] = [count[0] for count in c.most_common()[:-6:-1]]

    return result


def suggestc_text(value, **options):
    """Suggest a value for  the given value that violates the constraint.
    """
    null = options.get('missing_values', DEFAULT_MISSING_VALUES)[0]
    return null


def suggestd_text(value, **options):
    """Suggest a value in the given datatype.
    """
    null = options.get('missing_values', DEFAULT_MISSING_VALUES)[0]
    return null
