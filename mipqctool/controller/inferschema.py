
import os

from mipqctool.model.qcfrictionless import QCtoDC, CdeDict, QcTable
from mipqctool.controller.tablereport import TableReport

class InferSchema(object):   

    def __init__(self, table, csvname, sample_rows=100, maxlevels=10, cdedict=None, na_empty_strings_only=False):
        """Class for infering a dataset's schema which comes in csv file.
         Arguments:
         :param table: a QcTable holding the dataset csv data.
         :param csvname: a string with the filename of the dataset csv.
         :param sample_rows: number of rows that are going to be used for dataset's schema inference
         :param maxlevel: number of unique values in order to one infered variable to be considered as nominal(categorical)
                          above that number the variable will be considered as a text data type.
         :param cdedict: A CdeDict object containg info about all CDE variables
        """
        self.__table = table
        self.__csvname = csvname
        self.__table.infer(limit=sample_rows, maxlevels=maxlevels, na_empty_strings_only=na_empty_strings_only)
        self.__suggestions = None
        if cdedict:
            self.__cdedict = cdedict
            self.__tablereport = TableReport(self.__table, id_column=1)

    @property
    def tablereport(self):
        return self.__tablereport

    def suggest_cdes(self, threshold):
        """Arguments:
        :param threshold: 0-1 similarity threshold, below that not a cde is suggested """
        if self.__cdedict:
            suggestions = {}
            for name, columnreport in self.__tablereport.columnreports.items():
                var_name = columnreport.name
                cde = self.__cdedict.suggest_cde(columnreport, threshold=threshold)
                if cde:
                    suggestions[var_name] = [cde.code, cde.conceptpath]
                else:
                    suggestions[var_name] = [None, None]
            self.__suggestions = suggestions
        else:
            raise Exception('Error with the CDE dictionary')
    
    def export2excel(self, filepath):
        qctodc = QCtoDC(self.__table.schema.descriptor, self.__csvname, self.__suggestions)
        qctodc.export2excel(filepath)

    def expoct2qcjson(self, filename):
        self.__table.schema.save(filename)

    @classmethod
    def from_disc(cls, csvpath,  sample_rows=100, maxlevels=10, cdedict=None, na_empty_strings_only=False):
        """
        Constructs an InferSchema from loading a csv file from local disc.
        Arguments:
        :param csvpath: string filepath of the csv
        :param sample_rows: number of rows that are going to be used for dataset's schema inference
        :param maxlevel: number of unique values in order to one infered variable to be considered as nominal(categorical)
                         above that number the variable will be considered as a text data type.
        :param cdedict: A CdeDict object containg info about all CDE variables
        """
        
        dataset = QcTable(csvpath, schema=None)
        csvname = os.path.basename(csvpath)
        return cls(table=dataset, csvname=csvname,
                   sample_rows=sample_rows,maxlevels=maxlevels,
                   cdedict=cdedict, na_empty_strings_only=na_empty_strings_only)



    