# -*- coding: utf-8 -*-
# qcschema.py

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from tableschema import Schema, exceptions
from .qcfield import QcField
from . import config, qctypes
from .config import LOGGER

config.debug(True)


class QcSchema(Schema):

    def __init__(self, descriptor={}, strict=False):
        super().__init__(descriptor, strict)

        # overide __build and replace Fields objects
        # with QcFields ones
        self.__build()

    def infer(self, rows, headers=1,
              confidence=0.75, maxlevels=10):
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
        for index, row in enumerate(rows):
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
                rv = guesser.infer(value)
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

        return descriptor

    @property
    def fields_names(self):
        """Schema's field names
        # Returns
            str[]: an array of field names
        """
        return [field.name for field in self.fields]

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



# Internal

_INFER_PRIORITY = [
    'date',
    'integer',
    'numerical',
    'text'
]


class _QcTypeGuesser(object):
    """Guess the type for a value returning a tuple of ('type', 'pattern', priority)
    """
    def infer(self, value):
        for priority, name in enumerate(_INFER_PRIORITY):
            infer = getattr(qctypes, 'infer_%s' % name)
            pattern = infer(value)
            if pattern != config.ERROR:
                return (name, pattern, priority)


class _QcTypeResolver(object):
    def get(self, results, uniques, maxlevels, confidence=0.75):
        """Guess the field type and returns a field descriptor dict.
        """
        variants = set(results)
        # only one candidate... that's easy.
        if len(variants) == 1:
            name = results[0][0]
            pattern = results[0][1]
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
            for result in results:
                # filter out the NANs
                if result[1] == 'nan':
                    continue
                elif counts.get(result):
                    counts[result] += 1
                else:
                    counts[result] = 1

            # tuple representation of 'counts' dict sorted by values
            sorted_counts = sorted(counts.items(),
                                   key=lambda item: item[1],
                                   reverse=True)
            # Allow also counts that are not the max, based on the confidence
            max_count = sorted_counts[0][1]
            sorted_counts = filter(lambda item:
                                   item[1] >= max_count * confidence,
                                   sorted_counts)
            # Choose the most specific data type
            sorted_counts = sorted(sorted_counts,
                                   key=lambda item: item[0][2])
            name = sorted_counts[0][0][0]
            describe = getattr(qctypes, 'describe_%s' % name)
            rv = describe(sorted_counts[0][0][1],
                          uniques=uniques,
                          maxlevels=maxlevels)
        return rv
