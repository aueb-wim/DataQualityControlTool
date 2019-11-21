# -*- coding: utf-8 -*-
# qcfield.py

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from tableschema import Field
from tableschema.exceptions import CastError
from . import config, qctypes
from .exceptions import DataTypeError, ConstraintViolationError
from .config import LOGGER
from .helpers import expand_qcfield_descriptor

config.debug(True)


class QcField(Field):
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
        if self.miptype == 'nominal':
            enum = self.constraints.get('enum', [])
            suggested = self.__suggestc_function(value, enum=enum)
        # for MIPTypes integer, numerical, text, date
        else:
            suggested = self.__suggestc_function(value)
        return suggested

    def suggestd(self, value):
        suggested = self.__suggestd_function(value)
        return suggested

    # Private
    def __get_suggestd_function(self):
        return getattr(qctypes, 'suggestd_%s' % self.miptype)

    def __get_suggestc_function(self):
        return getattr(qctypes, 'suggestc_%s' % self.miptype)
