#!/usr/bin/env python3
import os
import csv
import json
from collections import OrderedDict
from mipqctool.model.dcatalogue.node import Node


class CDEsController():

    def __init__(self, dict_schema,  pathology=None, version=None):
        """
        Arguments:
        :param dict_schema: dictionary from Data Catalogue spec json 
        :param pathology: the pathology name for the CDEs
        :param version: version of the pathology's CDEs
        """

        self.__cdes_l = []
        self.cdes_d = OrderedDict()
        if version and pathology:
            self.__name = '_'.join([pathology, version])
        else:
            self.__name = None
        self.rootnode = Node(dict_schema)#now rootnode has all tree hanging below it...
        self.__store_cdes_first()

    @property
    def cde_names(self):
        return self.__cdes_l
    
    #Traverses the CDE-tree and stores the CDEs in self.cdes_d & l
    def __store_cdes_first(self):
        self.__store_cdes(current=self.rootnode)
    def __store_cdes(self, current):
        if current:
            variables = current.variables
            for var in variables:
                self.__cdes_l.append(var.code)
                #self.cdes_d.update({var.label : var})#this is how u add a key-value pair to a Dictionary... Oh my...
                self.cdes_d[var.code] = var
            groups = current.children
            for child in groups:
                self.__store_cdes(current=child)
        else: return

    def save_csv_headers_only(self, folderpath):
        """
        Saves the cde names into a csv file as headers.
        The name of the csv is <pathology>_<cde_version>.csv
        """
        if self.__name:
            filename = self.__name + '.csv'
        else:
            filename = 'cde_variables.csv'
        filepath = os.path.join(folderpath, filename)
        with open(filepath, 'w') as csvfile:
            cdewriter = csv.writer(csvfile, delimiter=',')
            cdewriter.writerow(self.cde_names)

    @classmethod
    def from_disc(cls, filepath):
        #filename = os.path.basename(filepath)
        #basename = os.path.splitext(filename)[0]
        with open(filepath) as jsonfile:
            cde_data = json.load(jsonfile)
            return cls(cde_data)

