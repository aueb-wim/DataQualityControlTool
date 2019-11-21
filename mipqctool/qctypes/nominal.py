# -*- coding: utf-8 -*-
# nominal.py

from __future__ import division
from __future__ import print_function
from __future__ import absolute_import
from __future__ import unicode_literals

import operator
from collections import Counter, OrderedDict
from nltk import edit_distance


def profile_nominal(pairs):
    """Return stats for the nominal field

    Arguments:
    :param pairs: list with pairs (row, value)
    :return: dictionary with stats
    """
    result = {}
    values = [r[1] for r in pairs]
    c = Counter(values)
    result['top'], result['freq'] = c.most_common(1)[0]
    categories = list(c)
    categories.sort()
    result['categories'] = categories
    result['categories_num'] = len(categories)

    return result


def suggestc_nominal(value, **options):
    """Returns a  suggested correct value.

    Arguments:
    :param value: string value
    :param constraint: enum list of strings with the enumerations values
    :return: string, the enum value with
             Levenshtein distance <= 3
             In case of draw returns the element which is closer to the 
             begining of the list with the enumerations
    """
    enum = options.get('enum', [])
    con_upper = [item.upper() for item in enum]
    distances = {key: edit_distance(value.upper(), key) for key in con_upper}
    ordered_by_key = OrderedDict(sorted(distances.items(), key=lambda t: t[0]))
    min_dist = min(ordered_by_key.items(), key=operator.itemgetter(1))
    if min_dist[1] <= 3:
        suggested_upper = min_dist[0]
        suggested_index = con_upper.index(suggested_upper)
        return enum[suggested_index]
    else:
        return None


def suggestd_nominal(value, **options):
    """Suggest a value in the given datatype.
    """
    return None
