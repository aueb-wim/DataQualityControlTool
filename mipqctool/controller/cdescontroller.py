#!/usr/bin/env python3
import os
import csv
import json
from collections import OrderedDict
from mipqctool.model.qcfrictionless import FrictionlessFromDC, QcSchema
from mipqctool.exceptions import QCToolException


class CDEsController():

    def __init__(self, dict_schema, schema_type='dc', pathology=None, version=None):
        """
        Arguments:
        :param dict_schema: dictionary
        :schema_type: string,[dc] for Data Catalogue schema specification
                             [qc] for frictionless schema specification 
        :param pathology: the pathology name for the CDEs
        :param version: version of the pathology's CDEs
        """

        if version and pathology:
            self.__name = '_'.join([pathology, version])
        else:
            self.__name = 'cde_variables'

        if schema_type == 'dc':
            # convert it to frictionless
            convertor = FrictionlessFromDC(dict_schema)
            self.__schema = QcSchema(convertor.qcdescriptor)
        elif schema_type == 'qc':
            self.__schema = QcSchema(dict_schema)
        else:
            raise QCToolException('"{}" is not a valid value for argument schema_type. Please choose "dc" or "qc"'. format(schema_type))

    @property
    def cdedataset_name(self):
        return self.__name

    @property
    def cde_headers(self):
        return self.__schema.fields_names

    @property
    def dataset_schema(self):
        """Returns a QcSchema object for the CDE dataset"""
        return self.__schema

    def save_csv_headers_only(self, filepath):
        """
        Saves the cde names into a csv file as headers.
        The name of the csv is <pathology>_<cde_version>.csv
        """
        with open(filepath, 'w') as csvfile:
            cdewriter = csv.writer(csvfile, delimiter=',')
            cdewriter.writerow(self.cde_headers)

    @classmethod
    def from_disc(cls, filepath, schema_type='dc'):
        #filename = os.path.basename(filepath)
        #basename = os.path.splitext(filename)[0]
        with open(filepath) as jsonfile:
            cde_data = json.load(jsonfile)
            return cls(cde_data, schema_type=schema_type)

