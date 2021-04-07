from __future__ import division
from __future__ import print_function
from __future__ import absolute_import
from __future__ import unicode_literals

import os

import pytest

from mipqctool.controller.cdescontroller import CDEsController

JSON_PATH1 = 'tests/test_datasets/simple_dc_cdes.json'
JSON_PATH2 = 'tests/test_datasets/dementia_cdes_v3.json'

CDES1 = ['dataset', 'av45' , 'fdg', 'pib','minimentalstate', 'montrealcognitiveassessment', 
         'updrshy', 'updrstotal', 'agegroup', 'gender', 'handedness', 'subjectage', 'subjectageyears']


@pytest.mark.parametrize('jsonpath, csvpath', [
    (JSON_PATH1, 'tests/test_datasets/cde_headers_only.csv')
])
def test_save_csv_headers_only(jsonpath, csvpath):
    test = CDEsController.from_disc(jsonpath)
    test.save_csv_headers_only(csvpath)


@pytest.mark.parametrize('jsonpath, result', [
    (JSON_PATH1, CDES1)
])
def test_cde_names(jsonpath, result):
    test = CDEsController.from_disc(jsonpath)
    assert set(test.cde_headers) == set(result)