#!/usr/bin/env python3
import os
import csv
import json
from collections import OrderedDict
from mipqctool.model.dcatalogue.node import Node


class CDEsController():

    def __init__(self, pathology, version, dict_schema):
        """
        Arguments:
        :param pathology: the pathology name for the CDEs
        :param version: version of the pathology's CDEs
        :param dict_schema: dictionary from Data Catalogue spec json 
        """

        self.cdes_l = []
        self.cdes_d = OrderedDict()
        self.__name = '_'.join([pathology, version])
        self.rootnode = Node(dict_schema)#now rootnode has all tree hanging below it...
        self.store_cdes_first()
    
    #Traverses the CDE-tree and stores the CDEs in self.cdes_d & l
    def store_cdes_first(self):
        self.store_cdes(current=self.rootnode)
    def store_cdes(self, current):
        if current:
            variables = current.variables
            for var in variables:
                self.cdes_l.append(var.label)
                #self.cdes_d.update({var.label : var})#this is how u add a key-value pair to a Dictionary... Oh my...
                self.cdes_d[var.label] = var
            groups = current.children
            for child in groups:
                self.store_cdes(current=child)
        else: return

    def save_empty_csv(self, folderpath):
        filename = self.__name + '.csv'
        filepath = os.path.path.join(folderpath, filename)


    @classmethod
    def from_disc(cls, pathology, version, filepath):
        pass