from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import json
from tableschema import Schema, exceptions
from .qcfield import QcField
from . import config, qctypes
from .config import LOGGER


class FrictionlessFromDC(object):
    """This class is made for parsing a DC JSON metadata file and creating
    its corresponding Frictionless descriptor dictionary."""

    dict_dc = None

    def __init__(self, json_path):
        with open(json_path) as json_file:
            self.dict_dc = json.load(json_file)
        # generates the tree structure of the loaded DC json
        self.rootnode = Node(self.dict_dc)
        self.findtree(self.rootnode)

    def findtree(self, dict):
        """generates the tree structure of the loaded DC json."""
        pass


class DcVariable(object):
    """"""
    __conceptpath = ''

    def __init__(self, dcdescriptor, node):
        self.node = node
        self.__descriptor = dcdescriptor

        # get variable info coming from Data Cataloge
        # common variable info
        self.__code = self.__descriptor.get('code', '')
        self.__label = self.__descriptor.get('label', '')
        self.__description = self.__descriptor.get('description', '')
        self.__sql_type = self.__descriptor.get('sql_type', 'text')
        self.__type = self.__descriptor.get('type', 'text')
        self.__methodology = self.__descriptor.get('methodology', '')
        self.__units = self.__descriptor.get('units', '')
        self.__iscategorical = self.__descriptor.get('isCategorical', False)
        # for categorical case
        self.__enumerations = self.__descriptor.get('enumerations', [])
        # for numeric variables
        self.__maxvalue = self.__descriptor.get('maxValue', None)
        self.__minvalue = self.__descriptor.get('minValue', None)
        
        self.__find_conceptpath()

    def createqcfield(self):
        """Returns the descriptor of the corresponding QcField."""
        constraints = {}
        fdict = {
            'name': self.__code,
            'title': self.__label,
            'description': self.__description,
            'format': 'default',
        }

        if self.__type in ['real', 'numeric']:
            fdict['type'] = 'number'
            fdict['MIPType'] = 'numerical'

        elif self.__type in ['int', 'integer']:
            fdict['type'] = 'integer'
            if self.__iscategorical:
                fdict['MIPType'] = 'nominal'
            else:
                fdict['MIPType'] = 'integer'
        
        elif self.__type in ['nominal', 'binominal', 'multinominal']:
            fdict['MIPType'] = 'nominal'
            if self.__sql_type == 'int':
                fdict['type'] = 'integer'
            else:
                fdict['type'] = 'string'
        elif self.__type == 'text':
            fdict['MIPType'] = 'text'
            fdict['type'] = 'string'

        if self.__enumerations:
            constraints['enum'] = self.__get_enum()

        if self.__maxvalue:
            constraints['maximum'] =  int(self.__maxvalue)

        if self.__minvalue:
            constraints['minimum'] = int(self.__minvalue)
        
        if constraints:
            fdict['constraints'] = constraints

        return fdict
            



    def __get_enum(self):
        return [enum['label'] for enum in self.__enumerations]

    def __find_conceptpath(self):
        path = '/'.join([self.node.conceptpath, self.__code])
        self.__conceptpath = path


class Node(object):
    """"""
    parent = None
    # self.dcvariable = None # DcVariable object
    # self.code = None
    __children = []
    __variables = []
    __conceptpath = ''

    def __init__(self, dcdescriptor, parent=None):
        self.__descriptor = dcdescriptor
        self.__code = self.__descriptor.get('code', '')
        self.__description = self.__descriptor.get('description', '')
        self.__label = self.__descriptor.get('label', '')
        self.parent = parent
        self.__find_conceptpath()
        self.__create_variables()
        self.__create_children()

    @property
    def description(self):
        return self.__description

    @property
    def label(self):
        return self.__label

    @property
    def conceptpath(self):
        return self.__conceptpath

    @property
    def code(self):
        return self.__code

    @property
    def children(self):
        return self.__children

    @property
    def variables(self):
        return self.__variables

    @code.setter
    def code(self, val):
        self.__code = val
        self.dcvariable.code = val

    def __find_conceptpath(self):
        # does node has a parent?
        if self.parent:
            path = '/'.join([self.parent.conceptpath, self.code])
        # if not, this is the root node and use as conceptpath its code
        else:
            path = '/' + self.code
        self.__conceptpath = path

    def __create_variables(self):
        # get the list with the desc
        vars = self.__descriptor.get('variables', [])
        self.__variables = [DcVariable(var, self) for var in vars]

    def __create_children(self):
        groups = self.__descriptor.get('groups', [])
        self.__children = [Node(group, self) for group in groups]

    def create_fdiscriptor(self):
        """Returns a frictionless dictionary with the node info."""
        dict_info = {
            'code': self.code,
            'label': self.label,
            'description': self.description}
        return dict_info

