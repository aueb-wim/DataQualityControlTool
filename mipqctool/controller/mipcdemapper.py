
import os

from mipqctool.model.mapping import Mapping, CsvDB
from mipqctool.model.qcfrictionless import CdeDict, QcTable
from mipqctool.controller import CDEsController, TableReport, InferSchema
from mipqctool.exceptions import MappingError

class MipCDEMapper(object):
    """Class for handling a simple (one to one) mapping task 
    and creating  the mapping xml for mipmap engine. 
    
    :Arguments:
    :source path: the filepath of the source csv
    :target_path: the filepaht of the target csv
    :param sample_rows: number of sample rows for schema inferance of
                        source csv
    :param maxlevels: total unique string values in a column to be 
                      considered as categorical type in schema inference 
                      of the source csv file. 

    """
    def __init__(self, source_path, target_path, sample_rows, maxlevels):
        sourcedb = CsvDB('hospitaldb',[source_path], schematype='source')
        targetdb = CsvDB('CDEdb', [target_path], schematype='target')
        self.__target_filename = os.path.basename(target_path)
        self.__mapping = Mapping(sourcedb, targetdb)
        self.__srctbl = QcTable(source_path, schema=None)
        # inder the table schema
        self.__srctbl.infer(limit=sample_rows, maxlevels=maxlevels)
        # create table report for the source file
        self.__tblreport = TableReport(self.__srctbl)
        self.__src_headers = self.__srctbl.headers
        self.__cde_headers = targetdb.get_table_headers(self.__target_filename)
        self.__cde_mapped = []
        self.__cde_not_mapped = self.__cde_headers

    @property
    def sourcereport(self):
        return self.__tblreport

    @property
    def mapping(self):
        return self.__mapping


    def suggest_corr(self, cdedictpath, threshold):
        """
        Arguments:
        :param cdedictpath: file path for the cde dict xlsx file
        :param threshold: 0-1 similarity threshold, below that not a cde is suggested
        """
        cdedict = CdeDict(cdedictpath)
        cde_sugg_dict = {}        
        source_table = self.__srctbl.filename
        target_table = self.__target_filename
        for columnreport in self.__tblreport.columnreports:
            cde = cdedict.suggest_cde(columnreport, threshold=threshold)
            if cde and cde.code not in cde_sugg_dict.keys():
                cde_sugg_dict[cde.code] = columnreport.name
        for cde, source_var in cde_sugg_dict.items():
            source_paths = [(source_table, source_var, None)]
            target_path = (target_table, cde, None)
            expression = '.'.join([os.path.splitext(source_table)[0], source_var])
            try:
                self.__mapping.add_correspondence(source_paths=source_paths, target_path=target_path,
                                                  expression=expression)
                self.__cde_not_mapped.remove(cde)
                self.__cde_mapped.append(cde)
            # If a cde correspondance already exists then pass
            except MappingError:
                pass

    def add_correspondance(self, cde, source_cols, expression):
        pass

    def remove_correspondance(self, cde):
        pass

    def update_correspodance(self, cde, source_cols, expression):
        pass

    


