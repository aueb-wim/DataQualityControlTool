#!/usr/bin/env python3
import os
import csv
import json
from mipqctool.model.dcatalogue.node import *

class CDEsController():

    def __init__(self, filepath):
        self.cdes_l = []
        self.cdes_d = {}
        if filepath:
            name = os.path.basename(filepath)
            #self.cde_label.config(text=name)
            self.cde_file_path = os.path.abspath(filepath)
            #now lets load the JSON
            with open(self.cde_file_path) as json_file:
                dict_schema = json.load(json_file)
            self.rootnode = Node(dict_schema)#now rootnode has all tree hanging below it...
            self.store_cdes_first()
        else:
            self.cde_file_path = None
            #self.cde_label.config(text='Not Selected')
    
    #Traverses the CDE-tree and stores the CDEs in self.cdes_d & l
    def store_cdes_first(self):
        self.store_cdes(current=self.rootnode)
    def store_cdes(self, current):
        if current:
            variables = current.variables
            for var in variables:
                self.cdes_l.append(var.label)
                self.cdes_d.update({var.label : var})#this is how u add a key-value pair to a Dictionary... Oh my...
            groups = current.children
            for child in groups:
                self.store_cdes(current=child)
        else: return