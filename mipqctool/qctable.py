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
from collections import defaultdict


class QcTable(Table):
    def __init__(self, source, **kargs):
        super().__init__(source, **kargs)
        self.__tableprofiler = None

    @property
    def tableprofiler(self):
        return self.__tableprofiler

    def infer(self, limit=100, maxlevels=10, confidence=0.75):
        if self._Table__schema is None or self._Table__headers is None:

            # Infer (tabulator)
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

    def iter_raw(self):
        stream = self._Table__stream
        stream.open()
        try:
            for row in stream.iter():
                yield row
        except:
            raise Exception('Oops! Something is not right in the csv file')
        finally:
            stream.close()

