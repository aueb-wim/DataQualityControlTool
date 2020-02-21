# -*- coding: utf-8 -*-
# qcfield.py

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from tableschema import Field
from tableschema.exceptions import CastError
from tableschema.config import DEFAULT_FIELD_FORMAT
from . import config, qctypes
from .exceptions import DataTypeError, ConstraintViolationError
from .config import LOGGER
from .helpers import expand_qcfield_descriptor

config.debug(True)


class QcField(Field):
    """This class holds metadata about a dataset column.
    Those metadata are the data type and constraints and are
    described in the descriptor dictionary.
    Based on those metadata the class can validate a given value
    and if there is a violation then can suggest a correction.
    There are 2 types of violations: datatype violation and constraint
    violation.
    """
    def __init__(self, descriptor, **kwargs):
        """
        Arguments:
        :param descriptor: dict with field descriptor
        :param missing_values: list with missing values
        """
        super().__init__(descriptor, **kwargs)
        descriptor = expand_qcfield_descriptor(descriptor)
        self._Field__descriptor = descriptor
        self.__suggestd_function = self.__get_suggestd_function()
        self.__suggestc_function = self.__get_suggestc_function()

    @property
    def miptype(self):
        return self.descriptor.get('MIPType')

    def validate(self, value):
        type_error_msg = ('Field "{field.name}" can\'t cast value "{value}" '
                          'for type "{field.type}" with format "{field.format}"'
                          ).format(field=self, value=value)
        try:
            self.cast_value(value, constraints=True)
            return value
        except CastError as e:
            if str(e) == type_error_msg:
                raise DataTypeError(str(e))
            else:
                raise ConstraintViolationError(str(e))

    def suggestc(self, value):
        """Returns a suggestion in case of a constraint violation
        """
        missing_values = self._Field__missing_values
        if self.miptype == 'nominal':
            # in this case we need to get the enumarations from the
            # constraints dictionary
            enum = self.constraints.get('enum', [])
            suggested = self.__suggestc_function(value,
                                                 enum=enum,
                                                 missing_values=missing_values)
        # for MIPTypes integer, numerical, text, date
        else:
            suggested = self.__suggestc_function(value,
                                                 missing_values=missing_values)
        return suggested

    def suggestd(self, value):
        """Returns a suggestion in case of a datatype violation
        """
        formatd = self.descriptor.get('format', DEFAULT_FIELD_FORMAT)
        missing_values = self._Field__missing_values
        suggested = self.__suggestd_function(value,
                                             missing_values=missing_values,
                                             format=formatd)
        # Datatype corrected, let's check if violates a constraint
        try:
            suggestedfinal = self.validate(suggested)
        except ConstraintViolationError:
            suggestedfinal = self.suggestc(suggested)
        return suggestedfinal

    # Private
    def __get_suggestd_function(self):
        return getattr(qctypes, 'suggestd_%s' % self.miptype)

    def __get_suggestc_function(self):
        return getattr(qctypes, 'suggestc_%s' % self.miptype)
