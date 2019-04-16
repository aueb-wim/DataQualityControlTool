# -*- coding: utf-8 -*-
# nominal.py

from __future__ import division
from __future__ import print_function
from __future__ import absolute_import
from __future__ import unicode_literals

from collections import Counter


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
