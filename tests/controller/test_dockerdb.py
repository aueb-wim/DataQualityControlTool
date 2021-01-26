from __future__ import division
from __future__ import print_function
from __future__ import absolute_import
from __future__ import unicode_literals

import pytest

from mipqctool.controller.dockerdb import DockerDB, find_xtport

@pytest.mark.parametrize('name, port, password, result', [
    ('demo_postgres', '75432', '1234', '45432')
])
def test_db_create(name, port, password, result):
    test = DockerDB(name, port, password)


@pytest.mark.parametrize('stringinput, result', [
    ('0.0.0.0:3245->3214', '3245')
])
def test_find_xtport(stringinput, result):
    assert find_xtport(stringinput) == result
