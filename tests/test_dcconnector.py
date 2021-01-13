from __future__ import division
from __future__ import print_function
from __future__ import absolute_import
from __future__ import unicode_literals

import os
import json
from unittest.mock import Mock, PropertyMock

import pytest

from mipqctool.dcatalogue import DcConnector

THISFILEDIR = os.path.dirname(os.path.realpath(__file__))

DCALLJSONPATH = os.path.join(THISFILEDIR,
                             'test_datasets',
                             'all_pathologies.json')

DCPATHOLOGYPATH1 = os.path.join(THISFILEDIR,
                                'test_datasets',
                                'dementia_cdes_v3.json')

PATHOLOGY_NAMES = ['dementia', 'mentalhealth', 'ftract',
                   'tbi', 'epilepsy', 'anatomy', 'msc',
                   'depression']

TBI_VERIONS = ['v5', 'v61']



@pytest.mark.parametrize('alljsonfile, pathologynames, status_code', [
    (DCALLJSONPATH, PATHOLOGY_NAMES, 200)
])
def test_getpathologies(alljsonfile, pathologynames, status_code):
    with open(alljsonfile) as f:
        alljson = json.load(f)
    dcrequest = Mock()
    dcrequest.json.return_value = alljson
    type(dcrequest).status_code = PropertyMock(return_value=200)
    test = DcConnector(dcrequest)
    assert test.pathology_names == pathologynames
    assert test.status_code == status_code

@pytest.mark.parametrize('alljsonfile, pathology, result', [
    (DCALLJSONPATH, 'tbi', TBI_VERIONS)
])
def test_getversions(alljsonfile, pathology, result):
    with open(alljsonfile) as f:
        alljson = json.load(f)
    dcrequest = Mock()
    dcrequest.json.return_value = alljson
    type(dcrequest).status_code = PropertyMock(return_value=200)
    test = DcConnector(dcrequest)
    assert test.get_pathology_versions(pathology) == result



@pytest.mark.parametrize('alljsonfile, pathologyfile, name, version', [
    (DCALLJSONPATH, DCPATHOLOGYPATH1, 'dementia', 'v3')
])
def test_getjson(alljsonfile, pathologyfile, name, version):
    with open(alljsonfile) as f:
        alljson = json.load(f)
    dcrequest = Mock()
    dcrequest.json.return_value = alljson
    type(dcrequest).status_code = PropertyMock(return_value=200)
    with open(pathologyfile) as f:
        pathologyjson = json.load(f)

    test = DcConnector(dcrequest)
    assert test.getjson(name, version) == pathologyjson
