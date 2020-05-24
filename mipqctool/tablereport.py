# -*- coding: utf-8 -*-
# columnreport.py

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import os
from jinja2 import Environment, FileSystemLoader
from weasyprint import HTML
from collections import namedtuple
from .exceptions import TableReportError
from .columnreport import ColumnReport
from .qctable import QcTable
from . import config, qctypes
from .config import LOGGER

config.debug(True)

class TableReport(object):
    """This class is for creating a report in pdf and csv files
    """
    def __init__(self, table, id_column):
        """ Arguments:
            :param table: a QcTable object
        """

        # check if id_column exist and get its index
        try:
            self.__id_index = table.headers.index(id_column)

        except ValueError:
            raise TableReportError('{} is not included in csv headers'.format(id_column))

        else:
            self.__id_column = id_column
            self.__table = table
            # check if table has a schema else infer
            if not self.__table.schema:
                self.__table.infer()

            self.__columnreports = []
            self.__create_reports

            self.__corrected = False

    def __create_reports(self):
        """Create column reports."""
        for qcfield in self.__table.schema.fields:
            raw_values = self.__table.column_values(qcfield.name)
            column_report = ColumnReport(raw_values, qcfield)
            column_report.validate()
            column_report.suggest_corrections()
            # calc statistics without violation corrections
            column_report.calc_stats()
            self.__columnreports.append(column_report)

    def __collect_row_stats(self):
        # get the rows with no id
        # get the report of id column
        id_column_report = self.__columnreports[self.__id_index]
        rows_with_no_id = id_column_report.nulls_row_numbers

        # find rows with only id filled in and the total row number
        # find total nulls and invalid
        rows_with_only_id = id_column_report.filled_row_numbers
        total_rows = id_column_report.total_rows
        total_nulls = 0
        total_cerrors = 0
        total_derrors = 0
        for report in self.__columnreports:
            total_nulls += report.nulls_total
            total_cerrors += report.constraint_errors
            total_derrors += report.datatype_errors
            if report.qcfield.name == self.__id_column:
                continue
            else:
                rows_with_only_id = rows_with_only_id - report.filled_row_numbers
                if report.total_rows > total_rows:
                    total_rows = report.total_rows
