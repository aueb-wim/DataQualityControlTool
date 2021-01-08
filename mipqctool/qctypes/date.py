# -*- coding: utf-8 -*-
# date.py

from __future__ import division
from __future__ import print_function
from __future__ import absolute_import
from __future__ import unicode_literals

import re
import datetime
from collections import Counter, OrderedDict
from tableschema.config import DEFAULT_FIELD_FORMAT
from ..config import ERROR, LOGGER, DEFAULT_DATE_FORMAT
from ..config import DEFAULT_MISSING_VALUES


def infer_date(value, **options):
    """Find if the given string value it represents a date.
    """
    result = None
    datetype = None
    sep = None
    year = None
    for priority, regex in enumerate(_PRIORITY_DATES, 1):
        match = re.match(regex, str(value), flags=re.UNICODE)
        if match:
            datetype = priority
            sep = match.group('sep')
            if len(match.group('year')) == 4:
                year = '%Y'
            break
    if datetype and year:
        if datetype == 1:
            result = '%d' + sep + '%m' + sep + year
        elif datetype == 2:
            result = '%m' + sep + '%d' + sep + year
        elif datetype == 3:
            result = year + sep + '%m' + sep + '%d'
        elif datetype == 4:
            result = '%d' + sep + '%b' + sep + year
        elif datetype == 5:
            result = '%d' + sep + '%B' + sep + year
        elif datetype == 6:
            result = '%b' + sep + '%d' + sep + year
        elif datetype == 7:
            result = '%B' + sep + '%d' + sep + year
    else:
        result = ERROR
    return result


def describe_date(pattern, **options):
    """Return a descriptor object based on given pattern.

    Arguments:
    :param pattern: string with qctype pattern
    :return: dictionary descriptor
    """
    match = re.match(_PAT, pattern, flags=re.UNICODE)
    if match:
        return {
            'type': 'date',
            'format': pattern,
            'MIPType': 'date'
        }
    else:
        return ERROR


def profile_date(pairs, **options):
    """Return stats for the date field

    Arguments:
    :param pairs: list with pairs (row, value)
    :return: dictionary with stats
    """
    result = OrderedDict()
    # Get the values in an numpy array
    values = [r[1] for r in pairs]
    c = Counter(values)
    result['mode'], result['freq'] = c.most_common(1)[0]
    result['min'] = min(values)
    result['max'] = max(values)

    return result


def suggestd_date(value, **options):
    """Suggest a new value in case of datatype violation.
    Tries to return a value in the given format date

    Arguments:
    :param value: string
    :param format: string, for date is a python date pattern like %d/%m/%y
    :return: date or None
    """
    null = options.get('missing_values', DEFAULT_MISSING_VALUES)[0]
    formatd = options.get('format', DEFAULT_DATE_FORMAT)
    if formatd == DEFAULT_FIELD_FORMAT:
        formatd = DEFAULT_DATE_FORMAT
    datepattern = infer_date(value)
    if datepattern != ERROR:
        newvalue = datetime.datetime.strptime(value, datepattern).date()
        return newvalue.strftime(formatd)
    else:
        return null


def suggestc_date(value, **options):
    """Suggest a new value for the given value in case of constraint violation.

    Arguments:
    :param value: string
    :constraint: string, name of the violated constraint
    """
    null = options.get('missing_values', DEFAULT_MISSING_VALUES)[0]
    return null

# Internal

# Date regex expressions

# %d %m %Y, dd-mm-yyyy, dd/mm/yyyy,dd.mm.yyyy
DATE1 = (r'^\b(0?[1-9]|[12][0-9]|3[01])'
         r'(?P<sep>[- /.]?)(0?[1-9]|1[012])'
         r'(?P=sep)(?P<year>(19|20)?\d\d)\b$')
# %m %d %Y, mm-dd-yyyy
DATE2 = (r'^\b(0?[1-9]|1[012])'
         r'(?P<sep>[- /.]?)(0?[1-9]|[12][0-9]|3[01])'
         r'(?P=sep)(?P<year>(19|20)?\d\d)\b$')
# %Y %m %d, yyyy-mm-dd
DATE3 = (r'^\b(?P<year>(19|20)?\d\d)'
         r'(?P<sep>[- /.]?)(0?[1-9]|1[012])'
         r'(?P=sep)(0?[1-9]|[12][0-9]|3[01])\b$')
# %d %b %Y, dd-mon-yyyy
DATE4 = (r'^\b(0?[1-9]|[12][0-9]|3[01])'
         r'(?P<sep>[ -]?)'
         r'[^0-9\s~!@#$%^&*()_+=\\/\[\]{}\'\":;,.<>?\-]{3}'
         r'(?P=sep)(?P<year>(19|20)?\d\d)\b$')
# %d %B %Y, dd-month-yyyy
DATE5 = (r'^\b(0?[1-9]|[12][0-9]|3[01])'
         r'(?P<sep>[ -]?)'
         r'[^0-9\s~!@#$%^&*()_+=\\/\[\]{}\'\":;,.<>?\-]{3,15}'
         r'(?P=sep)(?P<year>(19|20)?\d\d)\b$')
# %b %d %Y, mon-dd-yyyy
DATE6 = (r'^\b[^0-9\s~!@#$%^&*()_+=\\/\[\]{}\'\":;,.<>?\-]{3}'
         r'(?P<sep>[ -]?)(0?[1-9]|[12][0-9]|3[01])'
         r'(?P=sep)(?P<year>(19|20)?\d\d)\b$')
# %B %d %Y
DATE7 = (r'^\b[^0-9\s~!@#$%^&*()_+=\\/\[\]{}\'\":;,.<>?\-]{3,15}'
         r'(?P<sep>[ -]?)(0?[1-9]|[12][0-9]|3[01])'
         r'(?P=sep)(?P<year>(19|20)\d\d)\b$')

_PRIORITY_DATES = [DATE1, DATE2, DATE3, DATE4,
                   DATE5, DATE6, DATE7]

_PAT = r'^%[bBmdYy](?P<sep>[ -/.]?)%[bBmd](?P=sep)%[bBmdYy]$'
