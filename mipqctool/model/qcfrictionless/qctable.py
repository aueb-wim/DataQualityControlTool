# -*- coding: utf-8 -*-
# qctable.py

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import os
import re
from csv import DictReader, Sniffer
from collections import OrderedDict

from tableschema import Table

from mipqctool.model.qcfrictionless import QcSchema
from mipqctool.exceptions import QCToolException


class QcTable(Table):
    """This class is designed for csv files only.
    """
    def __init__(self, source, schema, **kargs):
        super().__init__(source, **kargs)
        self.__source = source
        self.__filename = os.path.basename(source)
        self.__headers_4_mipmap = OrderedDict()
        # if csv file get headers (tabulator aka csv file)
        if not self._Table__storage:
            # used encoding utf-8-sig to remove the byte order mask (BOM)
            with open(source, 'r', encoding='utf-8-sig') as csv_file:
                # find the dialect of the csv file
                try:
                    dialect = Sniffer().sniff(csv_file.read(1024))
                except:
                    dialect = 'excel'
                # reset the seeker to the start of the file
                csv_file.seek(0)
                reader = DictReader(csv_file, dialect=dialect)
                self.__actual_headers = reader.fieldnames
        else:
            self.__actual_headers = None

        if self.__actual_headers:
            self.__create_headers_4_mipmap()

        # QcSchema
        if isinstance(schema, QcSchema):
            self._Table__schema = schema
            self.__metadata = True
        elif isinstance(schema, dict):
            self._Table__schema = QcSchema(schema)
            self.__metadata = True
        else:
            self.__metadata = False

    @property
    def source(self):
        """The file path of the dataset"""
        return self.__source

    @property
    def filename(self):
        """The filename of the csv file"""
        return self.__filename

    @property
    def raw_rows(self):
        return [row for row in self.iter(cast=False)]

    @property
    def with_metadata(self):
        """True if a schema metadata json is used"""
        return self.__metadata

    @property
    def actual_headers(self):
        return self.__actual_headers

    @property
    def headers4mipmap(self) -> list:
        """Returns an ordered dict {original header: mipmap header}."""
        return list(self.__headers_4_mipmap.values())

    @property
    def invalid_nominals(self) -> dict:
        """Returns nominal fields with invalid enumrations.
        An enumration is invalid if it is an SQL keyword or is 
        a string and starts with a digit.
        """
        return self._Table__schema.invalid_nominals
    
    @property
    def invalid_header_names(self):
        """Returns header names containg invalid characters"""
        return self._Table__schema.invalid_header_names

    def infer(self, limit=100, maxlevels=10, confidence=0.75, na_empty_strings_only=False):
        """Tries to infer the table schema only for csv file.
        Arguments:
        :param limit: number of rows to be used for infer
        :param maxlevels: number of levels or enumeration for nominal qctypes
        :param confidence: float how many casting errors are allowed
                           (as a ratio, between 0 and 1)
        :param na_empty_strings_only: boolean to infer only empty strings as NAs

        :returns: dict Table Schema descriptor
        """
        if self._Table__schema is None or self._Table__headers is None:

            # Infer (tabulator aka csv file)
            if not self._Table__storage:
                with self._Table__stream as stream:
                    if self._Table__schema is None:
                        self._Table__schema = QcSchema()
                        self._Table__schema.infer(stream.read(limit=limit),
                                                  headers=stream.headers,
                                                  maxlevels=maxlevels,
                                                  confidence=confidence,
                                                  na_empty_strings_only=na_empty_strings_only)
                    if self._Table__headers is None:
                        self._Table__headers = stream.headers

            # Infer (storage) NOT INFERING MIPTYPES!!
            else:
                super().infer(limit=limit, confidence=confidence)

        self.__infered = True
        return self._Table__schema.descriptor

    def column_values(self, name):
        """Return a list of all values of the given column."""
        try:
            column_index = self.actual_headers.index(name)
        except ValueError:
            raise QCToolException('"{}" is not a column name among headers.'.format(name))

        return [row[column_index] for row in self.raw_rows]

    def __create_headers_4_mipmap(self):
        regexp = r'[`~!@#$%^*&\-+=\s\{\}\[\]\<\>\./\\:;?\(\)\']'
        for header in self.actual_headers:
            self.__headers_4_mipmap[header] = re.sub(regexp, '_', header)
