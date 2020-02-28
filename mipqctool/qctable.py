# -*- coding: utf-8 -*-
# qctable.py

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from tableschema import Table
from tableschema.exceptions import CastError
from tabulator import Stream
from .qcschema import QcSchema
from .exceptions import QCToolException
from collections import defaultdict


class QcTable(Table):
    """This class is designed for csv files only.
    """
    def __init__(self, source, **kargs):
        super().__init__(source, **kargs)

    @property
    def raw_rows(self):
        return [row for row in self.iter(cast=False)]

    def infer(self, limit=100, maxlevels=10, confidence=0.75):
        if self._Table__schema is None or self._Table__headers is None:

            # Infer (tabulator aka csv file)
            if not self._Table__storage:
                with self._Table__stream as stream:
                    if self._Table__schema is None:
                        self._Table__schema = QcSchema()
                        self._Table__schema.infer(stream.sample[:limit],
                                                  headers=stream.headers, 
                                                  maxlevels=maxlevels,
                                                  confidence=confidence)
                    if self._Table__headers is None:
                        self._Table__headers = stream.headers

            # Infer (storage) NOT INFERING MIPTYPES!!
            else:
                super().infer(limit=limit, confidence=confidence)

        return self._Table__schema.descriptor

    def column_values(self, name):
        """Return a list of all values of the given column."""
        try:
            column_index = self._Table__schema.field_names.index(name)
        except ValueError:
            raise QCToolException('"{}" is not a column name among headers.')
        return [row[column_index] for row in self.raw_rows]
