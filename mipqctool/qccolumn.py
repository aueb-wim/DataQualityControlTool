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
    def __init__(self, raw_values, field_descriptor,
                 missing_values=config.DEFAULT_MISSING_VALUES):
        self.__raw_pairs = enumerate(raw_values)
        self.__validated_pairs = []
        self.__datatype_violated_pairs = []
        self.__constraint_violated_pairs = []
        self.__datatype_s = None
        self.__constraint_s = None
        self.__field = QcField(descriptor=field_descriptor,
                               missing_values=missing_values)
        self.__miptype = self.__field.miptype
        self.__profile = self.__get_profile_function()
        self.__missing_values = missing_values

    @property
    def miptype(self):
        return self.__miptype

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
        Suggestion = namedtuple('Suggestion', 'row, value, newvalue')
        if self.__miptype == 'date':
            datatype_s = []
            for pair in self.__datatype_violated_pairs:
                row = pair[0]
                value = pair[1]
                newvalue = self.__suggest(value)
                suggestion = Suggestion(row=row,
                                        value=value,
                                        newvalue=newvalue)
                datatype_s.append(suggestion)
        else:
            newvalue = self.__missing_values[0]
            datatype_s = [Suggestion(row=pair[0],
                          value=pair[1],
                          newvalue=newvalue)
                          for pair in self.__datatype_violated_pairs]

        constraint_s = [Suggestion(row=pair[0],
                                   value=pair[1],
                                   newvalue=self.__suggest(pair[1]))
                        for pair in self.__constraint_violated_pairs]
        self.__datatype_s = datatype_s
        self.__constraint_s = constraint_s

    # Private
    def __get_profile_function(self):
        return getattr(qctypes, 'profile_%s' % self.miptype)

    def __suggest(self, value):
        newvalue = self.__missing_values[0]
        suggested_value = self.__field.suggest(value)
        if suggested_value:
            newvalue = suggested_value
        return newvalue
