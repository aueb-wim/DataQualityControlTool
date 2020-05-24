# -*- coding: utf-8 -*-
# ColumnReport.py

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


class ColumnReport(object):
    """This class is used to hold statistical and validation data of values
    of a dataset column.
    """
    def __init__(self, raw_values, qcfield):
        """Arguments:
        :param raw_values: list of strings representing values of a column
        :param qcfield: QcField object
        """
        # Stores all the values of the column in a list of
        # tupples (row number, raw value)
        self.__raw_pairs = enumerate(raw_values)
        self.__corrected = False

        self.__stats = {}
        self.__not_nulls = None
        self.__null_total = None
        self.__null_rows = None
        self.__not_null_rows = None
        # list of tupples that have been validated
        self.__validated_pairs = []
        # list of tupples that have been corrected
        self.__corrected_pairs = []
        self.__datatype_violated_pairs = []
        self.__constraint_violated_pairs = []
        self.__dsuggestions = None
        self.__csuggestions = None
        # stats about datatype, constraint violations and
        # suggested corrections
        self.__success_total_d = 0
        self.__success_total_c = 0
        self.__failed_total_d = 0
        self.__failed_total_c = 0
        # Create QcField object and other relative variables
        # and functions
        self.__field = qcfield
        self.__miptype = self.__field.miptype
        self.__profile = self.__get_profile_function()
        self.__cast_value = self.__field.cast_value
        self.__missing_values = self.__field.missing_values

    @property
    def qcfield(self):
        """Returns the object QcField"""
        return self.__field

    @property
    def miptype(self):
        return self.__miptype

    @property
    def total_rows(self):
        return len(self.__raw_pairs)

    @property
    def datatype_errors(self):
        """Total datatype violations"""
        return len(self.__datatype_violated_pairs)

    @property
    def constraint_errors(self):
        """Total constraint violations"""
        return len(self.__constraint_violated_pairs)

    @property
    def stats(self):
        """Statistics dictionary, different keys per qctype"""
        return self.__stats

    @property
    def violated_rows(self):
        """set of row numbers with violations"""
        vrows = set([pair[0] for pair
                     in self.__constraint_violated_pairs])
        vrows.update([pair[0] for pair
                      in self.__datatype_violated_pairs])
        return vrows


    @property
    def nulls_total(self):
        """Total number of rows with nulls"""
        return self.__null_total

    @property
    def not_nulls_total(self):
        """Total number of rows with no nulls"""
        return self.__not_nulls

    @property
    def null_row_numbers(self):
        """Set of row numbers with nulls"""
        return set(self.__null_rows)

    @property
    def filled_row_numbers(self):
        """Set of row numbers filled with valid values"""
        return set(self.__not_null_rows)

    @property
    def corrected(self):
        """Are the violation corrections applied?"""
        return self.__corrected

    @property
    def dcorrections(self):
        """Returns the datatype corrections as set of (original, corrected)."""
        null = self.__missing_values[0]
        correctiontupples = [(sug[1], sug[2])
                             for sug in self.__dsuggestions
                             if sug[2] != null]
        return set(correctiontupples)

    @property
    def dnulls(self):
        """Returns the values with datatype vialations unable to correct."""
        null = self.__missing_values[0]
        values = [sug[1]
                  for sug in self.__dsuggestions
                  if sug[2] == null]
        return set(values)

    @property
    def ccorrections(self):
        "Returns the constraint corrections as set of (original, corrected)."
        null = self.__missing_values[0]
        correctiontupples = [(sug[1], sug[2])
                             for sug in self.__csuggestions
                             if sug[2] != null]
        return set(correctiontupples)

    @property
    def cnulls(self):
        """Returns the values with constraint vialations unable to correct."""
        null = self.__missing_values[0]
        values = [sug[1]
                  for sug in self.__csuggestions
                  if sug[2] == null]
        return set(values)

    def validate(self):
        """Search for datatype and constraint violations."""
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
        """Try to suggest corrections for the violeted values."""
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
        """Returns statistics about the valid values."""
        profiler = self.__get_profile_function()
        raw_pairs = self.__validated_pairs + self.__corrected_pairs
        casted_pairs = []
        rows_with_nulls = []
        rows_with_no_nulls = []
        total_rows_with_nulls = 0
        for pair in raw_pairs:
            casted_value = self.__field.cast_value(pair[1])
            if casted_value:
                casted_pairs.append((pair[0], casted_value))
                rows_with_no_nulls.append(pair[0])
            else:
                rows_with_nulls.append(pair[0])
                total_rows_with_nulls += 1
        stats = profiler(casted_pairs)
        self.__not_nulls = len(casted_pairs)
        self.__null_total = total_rows_with_nulls
        self.__null_rows = rows_with_nulls
        self.__not_null_rows = rows_with_no_nulls
        self.__stats = stats

    def apply_corrections(self):
        """Apply the suggested corrections for both types of violations"""
        # NOTE corrections may include null values as suggestions
        datatypes = [(sd.row, sd.newvalue) for sd in self.__dsuggestions]
        constraints = [(sc.row, sc.newvalue) for sc in self.__csuggestions]
        self.__corrected_pairs = datatypes + constraints

    # Private
    def __get_profile_function(self):
        return getattr(qctypes, 'profile_%s' % self.miptype)

    def __suggestd(self, value):
        """Suggest a new value in case of datatype violation.
        Arguments:
        :param value: string
        :returns: string
        """
        null_string = self.__missing_values[0]
        suggested_value = self.__field.suggestd(value)
        if suggested_value != null_string:
            self.__success_total_d += 1
        else:
            self.__failed_total_d += 1

        return suggested_value

    def __suggestc(self, value):
        """Suggest a new value in case of constraint violation.
        Arguments:
        :param value: string
        :returns: string
        """
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
