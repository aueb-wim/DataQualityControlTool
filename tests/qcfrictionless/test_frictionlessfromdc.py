from __future__ import division
from __future__ import print_function
from __future__ import absolute_import
from __future__ import unicode_literals

import pytest
import json
from mipqctool.model.qcfrictionless import FrictionlessFromDC
from mipqctool.config import ERROR

TEST_JSON_PATH1 = 'tests/test_datasets/simple_dc_cdes.json'
TEST_JSON_PATH2 = 'tests/test_datasets/dementia_cdes_v3.json'


@pytest.mark.parametrize('dcjsonpath, frictjsonpath',[
    (TEST_JSON_PATH1, 'tests/test_datasets/dc2frictionless1.json'),
    (TEST_JSON_PATH2, 'tests/test_datasets/dc2frictionless2.json'),
])
def test_save2frictionless(dcjsonpath, frictjsonpath):
    with open(dcjsonpath) as json_file:
        dict_dc = json.load(json_file)
    test = FrictionlessFromDC(dict_dc)
    test.save2frictionless(frictjsonpath)


@pytest.mark.parametrize('dcjsonpath, result', [
    (TEST_JSON_PATH1, 13),
    (TEST_JSON_PATH2, 180)
])
def test_all_bellow_variables(dcjsonpath, result):
    with open(dcjsonpath) as json_file:
        dict_dc = json.load(json_file)
    test = FrictionlessFromDC(dict_dc)
    assert test.total_variables == result
