from __future__ import division
from __future__ import print_function
from __future__ import absolute_import
from __future__ import unicode_literals

import pytest
import json
from random import choice
from tests.mocker import ResultMocker
from mipqctool.qcfrictionless.frictionlessfromdc import Node
from mipqctool.config import ERROR

SIMPLE_DESCRIPTOR = {
    'code': 'rootcategory',
    'label': 'Root Category',
    'variables': [
        {
            'code': 'rootvar1',
            'label': 'Root var1',
            'sqltype': 'text'

        }
    ]
}
