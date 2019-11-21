# -*- coding: utf-8 -*-
# tableprofiler.py

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from copy import deepcopy
from collections import namedtuple
from tableschema.exceptions import CastError
from tableschema import Schema
from . import config

config.debug(True)
ErrorType = namedtuple('ErrorType', ['type', 'desc'])

class TableProfiler(object):

    def __init__(self, schema):
        """
        Arguments:
        :param schema: QcSchema descriptor - dictonary """

        self.__schema = Schema(schema)
        self.__unique_fields_cache = _create_unique_fields_cache(self.schema)
        self.__reset_table_stats()

    @property
    def schema(self):
        return self.__schema

    @property
    def invalid_rows(self):
        return self.__invalid_rows

    @property
    def rows_with_invalids(self):
        return self.__rows_with_invalids

    @property
    def rows_with_dublicates(self):
        return self.__rows_with_dublicates

    @property
    def rows_with_missing_pk(self):
        rows_missing_pk = list(self.__rows_with_missing_pk)
        rows_missing_pk.sort()
        return rows_missing_pk

    @property
    def rows_with_missing_required(self):
        rows_missing_rq = list(self.__rows_with_missing_required)
        rows_missing_rq.sort()
        return rows_missing_rq

    def validate(self, rows, headers):
        """Validate the table and calcs some table statistics.

        Arguments:
        :param rows: list of rows with the raw values of the table
                     ie. [[row1_value1, row1_value2, ..], ..]
        :param headers: list with the table header names
        :return: True if the table is valid
        """
        # initialize variables
        # reset the previous table statistics
        self.__reset_table_stats()
        self.__clear_unique_field_cache()
        check_uniques = False
        if self.__unique_fields_cache:
            check_uniques = True
        row_number = 1

        # Check table headers
        if headers != self.schema.field_names:
            desc = 'Table headers don\'t match schema field names'
            error = ErrorType('headers_mismatch', desc)
            self.__table_errors.append(error)

            return False

        # Check each row and update the table statistics
        for row in rows:
            validated_row = self._validate_row(row, check_uniques)
            if validated_row == config.ERROR:
                self.__invalid_rows.append(row_number)
            else:
                valid = validated_row[1]
                na_total = validated_row[2]
                dublicates = validated_row[3]
                if not valid:
                    # the validated row contains any invalid values
                    self.__rows_with_invalids.append(row_number)
                self.__total_na_per_row.append((row_number, na_total))
                if dublicates:
                    self.__rows_with_dublicates.append(row_number)
                self.__update_validated(validated_row, row_number)
            row_number += 1

        config.LOGGER.debug(self.__validated)
        # Check for missing values in primary keys and 'required'
        # type constraints
        self.__check_pk_constraints()

        # analyze table errors
        return self.__analyze_errors()

    def __update_validated(self, results, nrow):
        validated = results[0]
        dublicates = results[3]
        uniques = set()
        if dublicates:
            for name in dublicates:
                names = name.split(',')
                names = set(names)
                uniques.update(names)
        for index, r in enumerate(validated):
            if r['result'] == 'valid':
                self.__validated[index]['valids'].append((nrow, r['value']))
            elif r['result'] == 'invalid':
                self.__validated[index]['invalids'].append((nrow, r['value']))
            elif r['result'] == 'na':
                self.__validated[index]['na'].append(nrow)
            if r['name'] in uniques:
                self.__validated[index]['dublicates'].append(nrow)

    def _validate_row(self, row, check_uniques):
        """Validates a row.
        Arguments:
        :param row: a list with raw values
        :check_uniques: boolean, for fields with primary key
                        and unique constraints
        """
        fields = self.schema.fields
        missingvalues = self.schema.descriptor.get('missingValues',
                                                   config.DEFAULT_MISSING_VALUES)
        valid_row = True
        na_values = 0
        dublicates = []
        validated = []
        if len(row) != len(fields):
            return config.ERROR
        else:
            for index, value in enumerate(row):
                field = fields[index]
                validated.append({'name': field.name})
                try:
                    casted_value = field.cast_value(value)
                    validated[index]['value'] = casted_value
                    if casted_value:
                        validated[index]['result'] = 'valid'
                    else:
                        validated[index]['result'] = 'na'
                        na_values += 1
                except CastError:
                    valid_row = False
                    # case of required constraint violation
                    if value in missingvalues:
                        validated[index]['result'] = 'na'
                        na_values += 1
                    else:
                        validated[index]['value'] = value
                        validated[index]['result'] = 'invalid'
            if check_uniques:
                dublicates = self.__check_uniques(validated)
                if dublicates:
                    valid_row = False

        return validated, valid_row, na_values, dublicates

    def __check_uniques(self, validated):
        dublicates = []
        for indexes, cache in self.__unique_fields_cache.items():
            values = tuple(d.get('value') for i, d in enumerate(validated) if i in indexes)
            if not all(map(lambda value: value is None, values)):
                if values in cache['data']:
                    dublicates.append(cache['name'])
                cache['data'].add(values)

        return dublicates

    def __check_pk_constraints(self):
        primary_key_indexes = []
        required_indexes = []
        for index, field in enumerate(self.schema.fields):
            if field.name in self.schema.primary_key:
                primary_key_indexes.append(index)
            elif field.constraints.get('required'):
                required_indexes.append(index)

        for index in primary_key_indexes:
            rows = set(self.__validated[index]['na'])
            self.__rows_with_missing_pk.update(rows)

        for index in required_indexes:
            rows = set(self.__validated[index]['na'])
            self.__rows_with_missing_required.update(rows)

    def __analyze_errors(self):
        if self.__rows_with_invalids:
            desc = 'Table contains rows with invalid values'
            error = ErrorType('invalid_values', desc)
            self.__table_errors.append(error)
        if self.__invalid_rows:
            desc = 'Table contains rows with different length'
            error = ErrorType('invalid_row_length', desc)
            self.__table_errors.append(error)
        if self.__rows_with_dublicates:
            desc = 'Table have rows that violate the \"unique\" constraint'
            error = ErrorType('dublicate_values', desc)
            self.__table_errors.append(error)
        if self.__rows_with_missing_pk:
            desc = 'Table has rows with missing primary key'
            error = ErrorType('missing_pk', desc)
            self.__table_errors.append(error)
        if self.__rows_with_missing_required:
            desc = ('Table has rows with missing values'
                     'that have a \"required\" constraint')
            error = ErrorType('missing_values', desc)
            self.__table_errors.append(error)

        if self.__table_errors:
            return False
        else:
            return True

    def __clear_unique_field_cache(self):
        for item in self.__unique_fields_cache.values():
            item['data'] = set()

    def __reset_table_stats(self):
        self.__rows_with_invalids = []
        self.__invalid_rows = []
        self.__total_na_per_row = []
        self.__rows_with_dublicates = []
        self.__rows_with_missing_pk = set()
        self.__rows_with_missing_required = set()
        self.__table_errors = []
        self.__fieldstats = []
        self.__validated = [{'name': f.name,
                             'valids': [],
                             'invalids': [],
                             'na':[],
                             'dublicates':[]} for f in self.schema.fields]


# Internal

def _create_unique_fields_cache(schema):
    """
    ie {(0):{'name': 'id', 'data':set()}}
    """
    primary_key_indexes = []
    cache = {}

    # Unique
    for index, field in enumerate(schema.fields):
        if field.name in schema.primary_key:
            primary_key_indexes.append(index)
        if field.constraints.get('unique'):
            cache[tuple([index])] = {
                'name': field.name,
                'data': set(),
            }

    # Primary key
    if primary_key_indexes:
        cache[tuple(primary_key_indexes)] = {
            'name': ','.join(schema.primary_key),
            'data': set(),
        }

    return cache
