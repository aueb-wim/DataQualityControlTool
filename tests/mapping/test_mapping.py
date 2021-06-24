from __future__ import division
from __future__ import print_function
from __future__ import absolute_import
from __future__ import unicode_literals

import pytest

from mipqctool.model.mapping import CsvDB, Mapping
from mipqctool.config import ERROR

SOURCE_CSV_PATH1 = 'tests/test_datasets/nominal.csv'
TARGET_CSV_PATH1 = 'tests/test_datasets/simple.csv'
SIMPLE_HEADERS = ["id", "name", "diagnosis"]
NOMINAL_HEADERS = ['Patient_id', 'Variable_1', 'Variable_2']


def test_xml_creation():
    sourcedb = CsvDB('localdb', [SOURCE_CSV_PATH1])
    targetdb = CsvDB('cdedb', [TARGET_CSV_PATH1], schematype='target')
    test = Mapping(sourcedb, targetdb)
    sourcepaths= [('nominal.csv', 'Patient_id', None), ('nominal.csv', 'Variable_1', None)]
    target_path = ('simple.csv', 'id', None)
    expression = '(nominal.Patient_id + nominal.Variable_1)/2'
    test.add_corr(sourcepaths, target_path, expression)
    with open('tests/test_xml_files/testmapping.xml', 'w') as xmlfile:
        xmlfile.write(test.xml_string)
