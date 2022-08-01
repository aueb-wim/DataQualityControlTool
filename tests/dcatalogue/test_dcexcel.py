from __future__ import division
from __future__ import print_function
from __future__ import absolute_import
from __future__ import unicode_literals

import os
import pytest

from mipqctool.model.dcatalogue.dcexcel import DcExcel, ExcelVariable, DcGroup

DC_EXCEL_PATH = 'tests/test_datasets/invalid_dc_excel.xlsx'
DC_EXCEL_2_JSON_PATH = 'tests/test_datasets/dcexcel2json.xlsx'

VARIABLE_1 = {'code': 'subjectcode', 'name': 'subjectcode', 'type':'text', 'conceptpath': 'Demographics/petient/subjectcode'}
VARIABLE_2 = {'code': 'subjectageyears', 'name': 'subjectageyears', 'type':'integer', 'conceptpath': '/Demographics/petient/subjectageyears'}
VARIABLE_3 = {'code': 'rightstgsuperiortemporalgyrus', 'name': 'rightstgsuperiortemporalgyrus', 'type':'real', 'conceptpath': '/Neuroimaging/Brain Grey matter/temporal/rightstgsuperiortemporalgyrus'}
VARIABLE_4 = {'code': 'testvar1', 'name': 'Test var1', 'type':'text', 'conceptpath': 'testvar1'}

@pytest.mark.parametrize('variable, result', [
    ([{'name':'varialble1', 'type': 'nominal', 'values':'{"IN", "1.5t"}, {"2,4", "DC"}', 'conceptpath':'/root/var1'}], {'IN', '2,4'}),
])
def test_invalid_nominal(variable, result):
    test = ExcelVariable(*variable)
    assert set(test.invalid_enums) == result

@pytest.mark.parametrize('variable, result', [
    ({'code':'variable1', 'type': 'real',  'conceptpath':'root/var1'}, 1),
    ({'code':'variable1', 'type': 'real',  'conceptpath':'/root/var1'}, 1),
    ({'code':'variable1', 'type': 'real',  'conceptpath':'var1'}, 1),
    ({'code':'variable1', 'type': 'real',  'conceptpath':'variable1'}, 0),
    ({'code':'variable1', 'type': 'real',  'conceptpath':34 }, 1),
    #(VARIABLE_4, 0)
])
def test_invalid_conceptpath(variable, result):
    test = ExcelVariable(variable)
    assert len(test.errors) == result
    

@pytest.mark.parametrize('variable, result', [
    ({'code':'variable1', 'type': 'real',  'conceptpath':'brain anatomy/leftpart/variable1'}, '/brain anatomy/leftpart'),
    ({'code':'variable1', 'type': 'real',  'conceptpath':'/brain anatomy/leftpart/variable1'}, '/brain anatomy/leftpart'),
    ({'code':'variable1', 'type': 'real',  'conceptpath':'/variable1'}, ''),
    ({'code':'variable1', 'type': 'real',  'conceptpath':'variable1'}, ''),

])
def test_parent_conceptpath(variable, result):
    test = ExcelVariable(variable)
    assert test.parent_conceptpath == result


@pytest.mark.parametrize('variable, gparent_path,  result', [
    ({'code':'variable1', 'type': 'real',  'conceptpath':'brain anatomy/leftpart/variable1'}, '/brain anatomy', '/leftpart'),
    ({'code':'variable1', 'type': 'real',  'conceptpath':'/brain anatomy/leftpart/variable1'}, '/brain anatomy', '/leftpart'),
    ({'code':'variable1', 'type': 'real',  'conceptpath':'/leftpart/variable1'} ,'/leftpart', ''),
    ({'code': 'subjectcode', 'type':'text', 'conceptpath': 'Demographics/petient/subjectcode'}, '/Demographics', '/petient')
])
def test_parent_recursive_conceptpath(variable, gparent_path,  result):
    test = ExcelVariable(variable)
    test.update_rconceptpath(gparent_path)
    assert test.recursive_conceptpath == result


@pytest.mark.parametrize('variable, result', [
    ({'code':'variable1', 'type': 'real1',  'conceptpath':'/root/variable1'}, 1),
    ({'code':'variable1', 'type': 'not a valid type',  'conceptpath':'/root/variable1'}, 1),
])
def test_invalid_datatype(variable, result):
    test = ExcelVariable(variable)
    print(test.errors)
    assert len(test.errors) == result

@pytest.mark.parametrize('variable, result', [
    ({'type': 'real',  'conceptpath':'/root/variable1'}, 2),
    ({'code':'variable1', 'type': 'real'}, 1),
])
def test_missing_code(variable, result):
    test = ExcelVariable(variable)
    print(test.errors)
    assert len(test.errors) == result

@pytest.mark.parametrize('variable, result', [
    ({'code':'variable1', 'type': 'real',  'conceptpath':'/root/variable1', 'values': '1,1-1.5'}, 0),
    ({'code':'variable1', 'type': 'real',  'conceptpath':'/root/variable1'}, 0),
    ({'code':'variable1', 'type': 'real',  'conceptpath':'/root/variable1', 'values': '1,1'}, 1),
    ({'code':'variable1', 'type': 'real',  'conceptpath':'/root/variable1', 'values': '1,1-12-32'}, 1)
])
def test_invalid_range(variable, result):
    test = ExcelVariable(variable)
    assert len(test.errors) == result

@pytest.mark.parametrize('variables, result', [
    ([VARIABLE_1, VARIABLE_2, VARIABLE_3], '/')
])
def test_dcgroup_conceptpath(variables, result):
    var = [ExcelVariable(vardata) for vardata in variables]
    test = DcGroup('dementia', 'Dementia', var, parent=None, version='v1')
    assert test.conceptpath == result

@pytest.mark.parametrize('variables, result', [
    ([VARIABLE_1, VARIABLE_2, VARIABLE_3, VARIABLE_4], 1)
])
def test_dcgroup_number_variables(variables, result):
    var = [ExcelVariable(vardata) for vardata in variables]
    test = DcGroup('dementia', 'Dementia', var, parent=None, version='v1')
    assert len(test.variables) == result
    
@pytest.mark.parametrize('variables, result', [
    ([VARIABLE_1, VARIABLE_2, VARIABLE_3, VARIABLE_4], 2)
])
def test_dcgroup_number_children_variables(variables, result):
    var = [ExcelVariable(vardata) for vardata in variables]
    test = DcGroup('dementia', 'Dementia', var, parent=None, version='v1')
    print(test.children_variables)
    assert len(test.children_variables) == result


@pytest.mark.parametrize('filename, result', [
    (DC_EXCEL_2_JSON_PATH, 22)
])
def test_dcexcel_total_var(filename, result):
    test = DcExcel(filename)
    assert len(test.variable_list) == result

@pytest.mark.parametrize('filename, result', [
    (DC_EXCEL_2_JSON_PATH, 22)
])
def test_dcexcel(filename, result):
    test = DcExcel(filename)
    with open('tests/test_datasets/dcexcel2json.json', 'w') as jsonfile:
        jsonfile.write(test.create_dc_json('damentia', 'dementia', 'v1'))