from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from mipqctool.config import LOGGER

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

    @property
    def label(self):
        return self.__label

    @property
    def code(self):
        return self.__code

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
        return [enum['code'] for enum in self.__enumerations]

    def __find_conceptpath(self):
        path = '/'.join([self.node.conceptpath, self.__code])
        self.__conceptpath = path
