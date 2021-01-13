from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import json

from mipqctool.config import LOGGER

from .dcvariable import DcVariable

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