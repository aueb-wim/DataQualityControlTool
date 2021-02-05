from __future__ import division
from __future__ import print_function
from __future__ import absolute_import
from __future__ import unicode_literals

import os

import pytest

from mipqctool.controller.cdescontroller import CDEsController

TEST_JSON_PATH1 = 'tests/test_datasets/simple_dc_cdes.json'
TEST_JSON_PATH2 = 'tests/test_datasets/dementia_cdes_v3.json'

@pytest.mark.parametrize('jsonpath, csvpath', [
    (TEST_JSON_PATH1, 'tests/test_datasets/')
])
def test_save_csv_headers_only(jsonpath, csvpath):
    test = CDEsController.from_disc(jsonpath)
    test.save_csv_headers_only(csvpath)