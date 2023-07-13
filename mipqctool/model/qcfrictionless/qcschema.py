# -*- coding: utf-8 -*-
# qcschema.py

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals
from collections import namedtuple

import re

from tableschema import Schema, exceptions

from mipqctool.model.qcfrictionless import QcField
from mipqctool.model import qctypes
from mipqctool import config
from mipqctool.config import LOGGER, SQL_KEYWORDS

config.debug(True)


class QcSchema(Schema):
    """ QcSchema representation

     Arguments:
    :param descriptor: a frictionless json object schema (dict)
    :param strict: flag to specify validation behaviour:
        - if false, errors will not be raised but instead collected in `schema.errors`
        - if true, validation errors are raised immediately

    """

    def __init__(self, descriptor={}, strict=False):
        super().__init__(descriptor, strict)
        self.__infered = False
        self.__invalid_nominals = {}
        self.__invalid_header_names = []

        # overide __build and replace Fields objects
        # with QcFields ones
        self.__build()

    @property
    def fields_names(self):
        """Schema's field names
        # Returns
            str[]: an array of field names
        """
        return [field.name for field in self.fields]

    @property
    def invalid_header_names(self):
        """Returns header names containg invalid characters"""
        return self.__invalid_header_names

    @property
    def invalid_nominals(self) -> dict:
        """Returns nominal fields with invalid enumrations.
        An enumration is invalid if it is an SQL keyword or is 
        a string and starts with a digit.
        """
        return self.__invalid_nominals

    def infer(self, rows, headers=1,
              confidence=0.75, maxlevels=10,
              na_empty_strings_only=False):
        # Get headers
        if isinstance(headers, int):
            headers_row = headers
            while True:
                headers_row -= 1
                headers = rows.pop(0)
                if not headers_row:
                    break
        elif not isinstance(headers, list):
            headers = []

        if len(headers) > 0:
            self.__check_header_names(headers)

        # Get descriptor
        guesser = _QcTypeGuesser()
        resolver = _QcTypeResolver()
        descriptor = {'fields': []}
        type_matches = {}
        unique_values = {}
        missingvalues = set()
        for header in headers:
            descriptor['fields'].append({'name': header})
        LOGGER.info('{} of sample rows are used for table schema inference'.format(len(rows)))
        for row_number, row in enumerate(rows):
            # Normalize rows with invalid dimensions for sanity
            row_length = len(row)
            headers_length = len(headers)
            if row_length > headers_length:
                row = row[:len(headers)]
            if row_length < headers_length:
                diff = headers_length - row_length
                fill = [''] * diff
                row = row + fill
            # build a column-wise lookup of type matches
            for index, value in enumerate(row):
                # remove leading and trailing whitespacing
                value = value.strip()
                rv = guesser.infer(value, na_empty_strings_only=na_empty_strings_only)
                name = rv[0]
                pattern = rv[1]
                # collect unique values for possible nominal variable
                if pattern == 'text' or name == 'integer':
                    if unique_values.get(index):
                        unique_values[index].add(value)
                    else:
                        unique_values[index] = set()
                        unique_values[index].add(value)
                # collect the nans
                elif pattern == 'nan':
                    missingvalues.add(value)
                if type_matches.get(index):
                    type_matches[index].append(rv)
                else:
                    type_matches[index] = [rv]
        # choose a type/format for each column based on the matches
        for index, results in type_matches.items():
            uniques = unique_values.get(index)
            rv = resolver.get(results, uniques, maxlevels, confidence)
            descriptor['fields'][index].update(**rv)
        # case missing values have been found
        if len(missingvalues) > 0:
            # add the default missing value in any case
            missingvalues.update(set(config.DEFAULT_MISSING_VALUES))
            # sort missing values
            missing_sorted = list(missingvalues)
            missing_sorted.sort()
            # update the missing values
            descriptor['missingValues'] = list(missing_sorted)
        # case missing values not found use default
        elif len(missingvalues) == 0:
            descriptor['missingValues'] = config.DEFAULT_MISSING_VALUES

        # Save descriptor
        self._Schema__current_descriptor = descriptor
        self.__build()
        self.__infered = True

        return descriptor

    def update_fields_constraints(self, updates):
        """Updates the given fields for inferred schema only.
        Arguments:
        :param updates: dict with keys the field names and values dicts with the updates
                        {<name1>: {'minimum':value, 'maximum':value}
        """
        if self.__infered:
            for name, constraints in updates.items():
                for field in self._Schema__current_descriptor['fields']:
                    if field['name'] == name:
                        field['constraints'] = constraints
            self.__build()
            return True
        else:
            return False


    # Private methods

    def __check_nominals(self):
        invalid_nominals = {}
        for field in self.fields:
            if field.miptype == 'nominal':
                invalid_enums = []
                try:
                    enumerations = field.constraints['enum']
                    for enum in enumerations:
                        #LOGGER.debug('{} is type {}'.format(enum, type(enum)))
                        if isinstance(enum, str):
                            # if a enum is an integer number do nothing
                            if _checkInt(enum):
                                continue
                            # check if an enum is a sql keyword or starts with digit or is float
                            elif enum.upper() in SQL_KEYWORDS or enum[0].isdigit():
                                invalid_enums.append(enum)
                except KeyError:
                    pass

                if len(invalid_enums) > 0:
                    invalid_nominals[field.name] = invalid_enums
        self.__invalid_nominals = invalid_nominals

    def __check_header_names(self, headers):
        self.__invalid_header_names = [name for name in headers if not self.__is_valid_header_name(name)]


    def __is_valid_header_name(self, name):
        regex_patern = r'^[a-zA-Z_][a-zA-Z0-9_]*$'
        if re.match(regex_patern, name):
            return True
        else:
            return False

    def __build(self):
        self._Schema__build()
        # Repopulate fields witn QcField objects
        self._Schema__fields = []
        for field in self._Schema__current_descriptor.get('fields', []):
            missing_values = self._Schema__current_descriptor['missingValues']
            try:
                field = QcField(field, missing_values=missing_values)
            except exceptions.TableSchemaException as e:
                if self._Schema__strict:
                    raise e
                else:
                    field = False
            self._Schema__fields.append(field)
        self.__check_nominals()


# Internal

_INFER_PRIORITY = [
    'date',
    'integer',
    'numerical',
    'text'
]

_RESOLVE_PRIORITY = {
    'date':0,
    'text': 1,
    'numerical': 2,
    'integer': 3
}

Result = namedtuple('Result', ['name', 'pattern', 'priority'])

class _QcTypeGuesser(object):
    """Guess the type for a value returning a tuple of ('type', 'pattern', priority)
    """
    def infer(self, value, na_empty_strings_only=False):
        for priority, name in enumerate(_INFER_PRIORITY):
            infer = getattr(qctypes, 'infer_%s' % name)
            options={'na_empty_strings_only': na_empty_strings_only}
            pattern = infer(value, **options)
            resolve_priority = _RESOLVE_PRIORITY[name]
            if pattern != config.ERROR:
                return Result(name, pattern, resolve_priority)


class _QcTypeResolver(object):
    def get(self, results, uniques, maxlevels, confidence=0.75):
        """Guess the field type and returns a field descriptor dict.
        """
        variants = set(results)
        # only one candidate... that's easy.
        if len(variants) == 1:
            name = results[0].name
            pattern = results[0].pattern
            describe = getattr(qctypes, 'describe_%s' % name)
            # all are null, special case, infer it as text
            if pattern == 'nan':
                nulluniques = []
                nullmaxlevels = -100
                rv = describe('text',
                              uniques=nulluniques,
                              maxlevels=nullmaxlevels)
            else:
                rv = describe(pattern,
                              uniques=uniques,
                              maxlevels=maxlevels)
        else:
            counts = {}
            # {(name, pattern, priority):counts}
            for result in results:
                # filter out the NANs
                if result.pattern == 'nan':
                    continue
                elif counts.get(result):
                    counts[result] += 1
                else:
                    counts[result] = 1

            # tuple representation of 'counts' dict sorted by values
            # outputs a sorted list of tuples [(result:counts)]
            sorted_counts = sorted(counts.items(),
                                   key=lambda item: item[1],
                                   reverse=True)
            
            #max_count = sorted_counts[0][1]
            # Allow also counts that are not the max, based on the confidence 
            # (Not supported because there is no sense at the moment)
            #sorted_counts = filter(lambda item:
            #                       item[1] >= max_count * confidence,
            #                       sorted_counts)
            # choose the first two
            sorted_counts = sorted_counts[:2]
            # Choose the most specific data type
            sorted_counts = sorted(sorted_counts,
                                   key=lambda item: item[0].priority)
            name = sorted_counts[0][0].name
            describe = getattr(qctypes, 'describe_%s' % name)
            rv = describe(sorted_counts[0][0].pattern,
                          uniques=uniques,
                          maxlevels=maxlevels)
        return rv

def _checkInt(str):
    try:
        int(str)
        return True
    except ValueError:
        return False

