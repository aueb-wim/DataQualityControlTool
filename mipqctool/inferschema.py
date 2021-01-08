
from mipqctool.qcfrictionless import QCtoDC, CdeDict
from mipqctool.tablereport import TableReport

class InferSchema(object):   

    def __init__(self, table, csvname, sample_rows=100, maxlevels=10, cdedict=None):
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
        self.__table.infer(limit=sample_rows, maxlevels=maxlevels)
        self.__suggestions = None
        if cdedict:
            self.__cdedict = cdedict
            self.__tablereport = TableReport(self.__table, id_column=1)
        
    def suggest_cdes(self, threshold):
        if self.__cdedict:
            suggestions = {}
            for columnreport in self.__tablereport.columnreports:
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
    