# -*- coding: utf-8 -*-
# qccolumn.py

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from collections import namedtuple
from .qcfield import QcField
from . import config, qctypes
from .config import LOGGER
from .exceptions import DataTypeError, ConstraintViolationError

config.debug(True)


class QcColumn(object):
    """This class is used to hold statistical and validation data of values
    of a dataset column.
    """
    def __init__(self, raw_values, field_descriptor,
                 missing_values=config.DEFAULT_MISSING_VALUES):
        """ 
        """
        self.__raw_pairs = enumerate(raw_values)
        self.__stats = {}
        self.__validated_pairs = []
        self.__corrected_pairs = []
        self.__datatype_violated_pairs = []
        self.__constraint_violated_pairs = []
        self.__dsuggestions = None
        self.__csuggestions = None
        self.__success_total_d = 0
        self.__success_total_c = 0
        self.__failed_total_d = 0
        self.__failed_total_c = 0
        self.__field = QcField(descriptor=field_descriptor,
                               missing_values=missing_values)
        self.__miptype = self.__field.miptype
        self.__profile = self.__get_profile_function()
        self.__cast_value = self.__field.cast_value
        self.__missing_values = missing_values

    @property
    def miptype(self):
        return self.__miptype

    @property
    def datatype_errors(self):
        return len(self.__datatype_violated_pairs)

    @property
    def constraint_errors(self):
        return len(self.__constraint_violated_pairs)

    @property
    def stats(self):
        return self.__stats

    @property
    def dcorrections(self):
        null = self.__missing_values[0]
        correctiontupples = [(sug[1], sug[2]) 
                             for sug in self.__dsuggestions
                             if sug[2] != null]
        return set(correctiontupples)
    
    @property
    def dnulls(self):
        null = self.__missing_values[0]
        values = [sug[1]
                  for sug in self.__dsuggestions
                  if sug[2] == null]
        return set(values)

    @property
    def ccorrections(self):
        null = self.__missing_values[0]
        correctiontupples = [(sug[1], sug[2]) 
                             for sug in self.__csuggestions
                             if sug[2] != null]
        return set(correctiontupples)

    @property
    def cnulls(self):
        null = self.__missing_values[0]
        values = [sug[1]
                  for sug in self.__csuggestions
                  if sug[2] == null]
        return set(values)

    def validate(self):
        for raw_pair in self.__raw_pairs:
            try:
                self.__field.validate(raw_pair[1])
                self.__validated_pairs.append(raw_pair)
            except DataTypeError:
                self.__datatype_violated_pairs.append(raw_pair)
                continue
            except ConstraintViolationError:
                self.__constraint_violated_pairs.append(raw_pair)
                continue
        return True

    def suggest_corrections(self):
        self.__reset_sugg_stats()
        Suggestion = namedtuple('Suggestion', 'row, value, newvalue')
        dsuggestions = [Suggestion(row=pair[0],
                                   value=pair[1],
                                   newvalue=self.__suggestd(pair[1]))
                        for pair in self.__datatype_violated_pairs]

        csuggestions = [Suggestion(row=pair[0],
                                   value=pair[1],
                                   newvalue=self.__suggestc(pair[1]))
                        for pair in self.__constraint_violated_pairs]
        self.__dsuggestions = dsuggestions
        self.__csuggestions = csuggestions

    def calc_stats(self):
        profiler = self.__get_profile_function()
        raw_pairs = self.__validated_pairs + self.__corrected_pairs
        casted_pairs = []
        rows_with_nulls = []
        total_rows_with_nulls = 0
        for pair in raw_pairs:
            casted_value = self.__field.cast_value(pair[1])
            if casted_value:
                casted_pairs.append((pair[0], casted_value))
            else:
                rows_with_nulls.append(pair[0])
                total_rows_with_nulls += 1
        stats = profiler(casted_pairs)
        stats['not_nulls'] = len(casted_pairs)
        stats['null_total'] = total_rows_with_nulls
        stats['null_rows'] = rows_with_nulls
        self.__stats = stats

    def apply_corrections(self):
        # TODO not cast the value just return the string value
        datatypes = [(sd.row, sd.newvalue) for sd in self.__dsuggestions]
        constraints = [(sc.row, sc.newvalue) for sc in self.__csuggestions]
        self.__corrected_pairs = datatypes + constraints

    # Private
    def __get_profile_function(self):
        return getattr(qctypes, 'profile_%s' % self.miptype)

    def __suggestd(self, value):
        null_string = self.__missing_values[0]
        suggested_value = self.__field.suggestd(value)
        if suggested_value != null_string:
            self.__success_total_d += 1
        else:
            self.__failed_total_d += 1

        return suggested_value

    def __suggestc(self, value):
        null_string = self.__missing_values[0]
        suggested_value = self.__field.suggestc(value)
        if suggested_value != null_string:
            self.__success_total_c += 1
        else:
            self.__failed_total_c += 1

        return suggested_value

    def __reset_sugg_stats(self):
        self.__success_total_d = 0
        self.__success_total_c = 0
        self.__failed_total_d = 0
        self.__failed_total_c = 0
