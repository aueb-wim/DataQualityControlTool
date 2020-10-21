from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import json
from tableschema import Schema, exceptions
from .qcfield import QcField
from .. import config, qctypes
from ..config import LOGGER, DEFAULT_MISSING_VALUES


class FrictionlessFromDC(object):
    """This class is made for parsing a DC JSON metadata file and creating
    its corresponding Frictionless descriptor dictionary.
    
    Arguments:
    :param json_path: (str) the path of a datacatalue produced json file

    """
    __qcdescriptor = None

    def __init__(self, dcjson):
        # generates the tree structure of the loaded DC json
        LOGGER.info('Finding variable tree...')
        self.rootnode = Node(dcjson)
        self.__dc2qc()

    @property
    def total_variables(self):
        return len(self.rootnode.all_below_qcdesc)

    @property
    def qcdescriptor(self):
        return self.__qcdescriptor

    def save2frictionless(self, filepath):
        with open(filepath, 'w') as jsonfile:
            json.dump(self.__qcdescriptor, jsonfile)

    def __dc2qc(self):
        self.__qcdescriptor = {
            'fields': self.rootnode.all_below_qcdesc,
            'missingValues': DEFAULT_MISSING_VALUES
        }




class DcVariable(object):
    """A class to store data from a Data Catalogue json"""
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

    @property
    def conceptpath(self):
        return self.__conceptpath

    def createqcfield(self):
        """Returns the descriptor of the corresponding QcField."""
        constraints = {}
        fdict = {
            'name': self.__code,
            'title': self.__label,
            'description': self.__description,
            'format': 'default',
            'conceptPath': self.conceptpath
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
    __children = []
    __variables = []
    __conceptpath = ''
    __qcdescriptors = []
    __all_below_qcdesc = []

    def __init__(self, dcdescriptor, parent=None):
        self.__descriptor = dcdescriptor
        self.__code = self.__descriptor.get('code', '')
        self.__description = self.__descriptor.get('description', '')
        self.__label = self.__descriptor.get('label', '')
        self.__parent = parent
        self.__find_conceptpath()
        self.__create_variables()
        self.__create_children()

        if parent:
            self.__give_qcdesc_to_parent()
            self.__qcdescriptors = None
            self.__all_below_qcdesc = None
        else:
            LOGGER.debug('This node is the root. Adding root variables..')
            self.add_below_qcdesc(self.qcdescriptors)
            LOGGER.debug('Total variables found on the tree: {}'.format(len(self.__all_below_qcdesc)))

    @property
    def parent(self):
        return self.__parent

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

    @property
    def qcdescriptors(self):
        return self.__qcdescriptors

    @property
    def all_below_qcdesc(self):
        return self.__all_below_qcdesc

    def add_below_qcdesc(self, qcdescs):
        self.__all_below_qcdesc = self.__all_below_qcdesc + qcdescs

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
        self.__qcdescriptors = [var.createqcfield() for var in self.__variables]

    def __create_children(self):
        groups = self.__descriptor.get('groups', [])
        self.__children = [Node(group, self) for group in groups]

    def __give_qcdesc_to_parent(self):
        self.parent.add_below_qcdesc(self.qcdescriptors + self.all_below_qcdesc)