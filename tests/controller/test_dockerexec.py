from __future__ import division
from __future__ import print_function
from __future__ import absolute_import
from __future__ import unicode_literals

import os
from pathlib import Path

import pytest

from mipqctool.controller.dockerexec import DockerExec

FILE_PATH = os.path.abspath(os.path.dirname(__file__))
THISPATH = Path(FILE_PATH)
PARENTPATH = str(THISPATH.parent)

MAPPING1 = os.path.join(PARENTPATH, 'test_mappings', 'mapping')
SOURCE1 = os.path.join(PARENTPATH, 'test_mappings', 'source')
OUTPUT1 = os.path.join(PARENTPATH, 'test_mappings', 'output')
TARGET1 = os.path.join(PARENTPATH, 'test_mappings', 'target')


@pytest.mark.parametrize('name, port, password, mapping, source, target, output', [
    ('demo_postgres', '54633', '1234', MAPPING1, SOURCE1, TARGET1, OUTPUT1)
])
def test_dockermipmap(name, port, password, mapping, source, target, output):
    test = DockerExec(name, port, password, mapping, source, target, output)