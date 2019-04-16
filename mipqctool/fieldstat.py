# -*- coding: utf-8 -*-
# fieldstat.py

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from . import qctypes


class FieldStat(object):

    def __init__(self, descriptor, **options):

        # Set attributes
        self.__stats = None
        self.__descriptor = descriptor

    @property
    def stats(self):
        return self.__stats

    @property
    def descriptor(self):
        return self.__descriptor

    def get(self, valid, invalid, na):
        """Returns the statistics of a field in a table.

        Arguments:
        :param descriptor: dictionary
        :param valid: list valid values, pair of (row, value)
        :param invalid: list invalid values, (row, value)
        :param na: list of rows with nans
        :return: dict with statistics
        """
        result = self.__getcommon(valid, invalid, na)
        profiler = self.__get_stat_function()
        if valid:
            result.update(profiler(valid))
        self.__stats = result

        return self.__stats

    # Private

    def __getcommon(self, valid, invalid, na):
        result = {}

        if valid:
            result['valid'] = len(valid)
        else:
            result['valid'] = 0

        if invalid:
            result['invalid'] = len(invalid)
        else:
            result['invalid'] = 0

        if na:
            result['na'] = len(na)
        else:
            result['na'] = 0

        result['total_rows'] = sum((result['valid'],
                                   result['invalid'],
                                   result['na']))
        validper = round(result['valid'] / result['total_rows'] * 100, 2)
        result['valid%'] = validper
        invalidper = round(result['invalid'] / result['total_rows'] * 100, 2)
        result['invalid%'] = invalidper
        result['na%'] = round(result['na'] / result['total_rows'] * 100, 2)

        return result

    def __get_stat_function(self):
        name = self.__descriptor.get('MIPType', 'text')
        return getattr(qctypes, 'profile_%s' % name)
