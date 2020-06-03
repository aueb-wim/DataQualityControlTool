from __future__ import division
from __future__ import print_function
from __future__ import absolute_import
from __future__ import unicode_literals

import sys
from random import randint
import mipqctool.config
from mipqctool.config import ERROR, LOGGER

mipqctool.config.debug(True)

THISMODULE = sys.modules[__name__]


def give_number(pattern=0):
    patterns = [
        'd.',
        'd,',
        'd. cm3',
        'd. %',
    ]
    return 'numerical', patterns[pattern], 2


def give_date(pattern=0):
    patterns = [
        '%d/%m/%Y',
        '%d-%m-%Y',
        '%m-%B-%Y',
        '%Y %B %d',
    ]
    return 'date', patterns[pattern], 0


def give_integer(pattern=0):
    patterns = [
        'd',
        'd cm3',
        'd%',
        'd euro'
    ]
    return 'integer', patterns[pattern], 1


def give_text(pattern=0):
    return 'text', 'text', 3


def give_nan(pattern=0):
    return 'text', 'nan', 3


class ResultMocker(object):
    def get_results(self, patterns, typecounts):
        results = []
        limit = patterns - 1
        for qctype, counts in typecounts.items():
            giver = getattr(THISMODULE, 'give_%s' % qctype)
            type_results = [giver(randint(0, limit)) for i in range(counts)]
            results.extend(type_results)
        return results
