# -*- coding: utf-8 -*-
# columnreport.py

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import os
import csv
from datetime import datetime
from jinja2 import Environment, FileSystemLoader
from weasyprint import HTML
from collections import namedtuple, Counter, defaultdict
from .exceptions import TableReportError
from .columnreport import ColumnReport
from .qctable import QcTable
from . import config, qctypes
from .config import LOGGER

from . import __version__

config.debug(True)


class TableReport(object):
    """This class is for creating a report in pdf and csv files
    """
    def __init__(self, table, id_column):
        """ Arguments:
            :param table: a QcTable object
            :param id_column: column number of dataset's primary key (id)
        """
        if not table.schema:
            table.infer()

        # check if id_column number exist and get its column name
        try:

            self.__id_column = table.schema.fields_names[id_column-1]

        except IndexError:
            raise TableReportError('{} column number is out of bounds'.format(id_column))

        else:
            self.__id_index = id_column - 1
            self.__table = table
            # check if table has a schema else infer

            self.__total_columns = len(self.__table.schema.field_names)
            self.__columns_quantiles = None
            self.__calc_columns_quantiles()

            self.__columnreports = []
            self.__total_rows = None
            self.__rows_only_id = None
            self.__rows_no_id = None
            self.__tvalid_columns = None
            self.__tfilled_columns = None
            self.__corrected = False

            self.__create_reports()
            self.__collect_row_stats()

    @property
    def total_rows(self):
        """Number of dataset's rows"""
        return self.__total_rows

    @property
    def corrected(self):
        """Are the correction applied?"""
        return self.__corrected

    @property
    def total_columns(self):
        """Number of dataset's columns"""
        return self.__total_columns

    @property
    def valid_rows_stats(self):
        """Dict with rows data validation overall stats"""
        return self.__calc_rstat_dict(columns='valid')

    @property
    def filled_rows_stats(self):
        """Dict with rows data completion overall stats"""
        return self.__calc_rstat_dict(columns='filled')

    def apply_corrections(self):
        for columnreport in self.__columnreports:
            columnreport.apply_corrections()
        self.__collect_row_stats()
        self.__corrected = True

    def save_corrected(self, path):
        if self.__corrected:
            list_new_values = (col.corrected_values for col in self.__columnreports)
            new_values = zip(*list_new_values)
            with open(path, 'w') as out:
                csv_out = csv.writer(out, quoting=csv.QUOTE_ALL)
                csv_out.writerow(self.__table.headers)
                for row in new_values:
                    csv_out.writerow(row)

    def printpdf(self, filepath):
        app_path = os.path.abspath(os.path.dirname(__file__))
        env_path = os.path.join(app_path, 'html')
        css_path = os.path.join(env_path, 'style.css')
        docs = []
        template_vars = self.__prepare_stat2pdf()
        env = Environment(loader=FileSystemLoader(env_path))
        if self.__corrected:
            template_file = 'dataset_report_verified.html'
        else:
            template_file = 'dataset_report.html'
        template = env.get_template(template_file)
        html_out = template.render(template_vars)
        docs.append(HTML(string=html_out).render(stylesheets=[css_path]))
        for columnreport in self.__columnreports:
            docs.append(HTML(string=columnreport.to_html()).render(stylesheets=[css_path]))

        all_pages = [p for doc in docs for p in doc.pages]
        docs[0].copy(all_pages).write_pdf(target=filepath)

    # private
    def __create_reports(self):
        """Create column reports."""
        for qcfield in self.__table.schema.fields:
            raw_values = self.__table.column_values(qcfield.name)
            column_report = ColumnReport(raw_values, qcfield)
            column_report.validate()
            self.__columnreports.append(column_report)

    def __collect_row_stats(self):
        # get the rows with no id
        # get the report of id column
        id_column_report = self.__columnreports[self.__id_index]
        rows_with_no_id = id_column_report.null_row_numbers

        # find rows with only id filled in and the total row number
        # find total nulls and invalid
        rows_with_only_id = id_column_report.filled_row_numbers
        total_rows = id_column_report.total_rows

        rows_invalid = []
        rows_nulls = []
        for report in self.__columnreports:
            rows_invalid.extend(list(report.invalid_rows))
            rows_nulls.extend(list(report.null_row_numbers))
            if report.qcfield.name == self.__id_column:
                continue
            else:
                rows_with_only_id = rows_with_only_id - report.filled_row_numbers
                if report.total_rows > total_rows:
                    total_rows = report.total_rows

        total_invalid_rows = len(set(rows_invalid))
        invalid_counter = Counter(rows_invalid)
        null_counter = Counter(rows_nulls)
        max_columns_per_row_ = {row: self.total_columns
                                for row in range(1, total_rows + 1)}
        # initialize valid and filled counters with max column
        # number per row. aka each row has all columns filled and valid
        valid_counter = Counter(max_columns_per_row_)
        filled_counter = Counter(max_columns_per_row_)

        # subtract the invalid to find the valid columns per row
        valid_counter.subtract(invalid_counter)
        # subtract the nulls to find the filled columns per row
        filled_counter.subtract(null_counter)

        self.__total_rows = total_rows
        self.__total_invalid_rows = total_invalid_rows

        self.__rows_only_id = rows_with_no_id
        self.__rows_no_id = rows_with_only_id
        self.__tvalid_columns = self.__calc_rows_per_columns(dict(valid_counter))
        self.__tfilled_columns = self.__calc_rows_per_columns(dict(filled_counter))

    def __calc_columns_quantiles(self):
        cquantiles = {}
        cquantiles['p99'] = self.total_columns - 1
        cquantiles['p75'] = round(self.total_columns * 75 / 100)
        cquantiles['p74'] = cquantiles['p75'] - 1
        cquantiles['p50'] = round(self.total_columns / 2)
        cquantiles['p49'] = cquantiles['p50'] - 1
        cquantiles['p25'] = round(self.total_columns * 25 / 100)
        cquantiles['p24'] = cquantiles['p25'] - 1
        self.__columns_quantiles = cquantiles

    def __calc_rows_per_columns(self, d):
        res = defaultdict(list)
        for key, val in d.items():
            res[val].append(key)
        result = {k: len(v) for (k, v) in res.items()}
        return result

    def __calc_rstat_dict(self, columns='filled'):
        stats = {}
        if columns == 'filled':
            dict_column = self.__tfilled_columns
        elif columns == 'valid':
            dict_column = self.__tvalid_columns

        for i in range(0, self.__columns_quantiles['p25']):
            key = columns + '_' + '0_24'
            stats[key] = stats.get(key, 0) + dict_column.get(i, 0)

        for i in range(self.__columns_quantiles['p25'], self.__columns_quantiles['p50']):
            key = columns + '_' + '25_49'
            stats[key] = stats.get(key, 0) + dict_column.get(i, 0)

        for i in range(self.__columns_quantiles['p50'], self.__columns_quantiles['p75']):
            key = columns + '_' + '50_74'
            stats[key] = stats.get(key, 0) + dict_column.get(i, 0)

        for i in range(self.__columns_quantiles['p75'], self.__total_columns):
            key = columns + '_' + '75_99'
            stats[key] = stats.get(key, 0) + dict_column.get(i, 0)

        key = columns + '_' + '100'
        stats[key] = dict_column.get(self.total_columns, 0)

        return stats

    def __prepare_stat2pdf(self):
        daterun = datetime.now()

        if self.__corrected:
            applied_corrections = 'Yes'
        else:
            applied_corrections = 'No'

        if self.__table.with_metadata:
            use_metadata = 'Yes'
        else:
            use_metadata = 'No'
        
        html_vars = {
            'datasetfile': self.__table.filename,
            'date_run': daterun.strftime("%d/%m/%Y %H:%M:%S"),
            'qcversion': __version__,
            'csvfilepath': self.__table.source,
            'use_metadata': use_metadata,
            'applied_corrections': applied_corrections,
            'only_ids': len(self.__rows_only_id),
            'only_ids_perc': round(len(self.__rows_only_id) / self.total_rows * 100, 2),
            'no_ids': len(self.__rows_no_id),
            'no_ids_perc': round(len(self.__rows_no_id) / self.total_rows * 100, 2),
            'total_columns': self.total_columns,
            'total_rows': self.total_rows,
            'total_invalid_rows': self.__total_invalid_rows
        }

        html_vars.update(self.filled_rows_stats)
        html_vars.update(self.valid_rows_stats)
        html_vars.update(self.__columns_quantiles)
        
        # calc the percentages for valid and filled row stats
        for item in self.filled_rows_stats.items():
            key_perc = item[0] + '_perc'
            html_vars[key_perc] = round(item[1] / self.total_rows * 100, 2)

        for item in self.valid_rows_stats.items():
            key_perc = item[0] + '_perc'
            html_vars[key_perc] = round(item[1] / self.total_rows * 100, 2)

        return html_vars

        
