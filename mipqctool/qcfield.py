# -*- coding: utf-8 -*-
# qcfield.py

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from tableschema import Field
from . import config
from .config import LOGGER

config.debug(True)


class QcField(Field):
    def __inin__(self, **kwargs):
        super().__init__(**kwargs)

    @property
    def miptype(self):
        return self.__descriptor.get('miptype')

    def _get_discribe_function(self):
        pass

    def __get_stat_function(self):
        pass
