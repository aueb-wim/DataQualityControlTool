
import os
from pathlib import Path
from collections import OrderedDict

from mipqctool.model.mapping import Mapping, CsvDB
from mipqctool.model.mapping.functions import ifstr
from mipqctool.model.qcfrictionless import QcTable
from mipqctool.controller import CDEsController, TableReport, DockerMipmap
from mipqctool.exceptions import MappingError
from mipqctool.config import LOGGER

DIR_PATH = os.path.dirname(os.path.abspath(__file__))
PATH = Path(DIR_PATH)
PARENTPATH= PATH.parent

class MipCDEMapper(object):
    """Class for handling a simple (one to one) mapping task 
    and creating  the mapping xml for mipmap engine. 
    
    :Arguments:
    :source path: the filepath of the source csv
    :cdescontroller: a CDEsController object containing info about the target CDE dataset
    :param sample_rows: number of sample rows for schema inferance of
                        source csv
    :param maxlevels: total unique string values in a column to be 
                      considered as categorical type in schema inference 
                      of the source csv file. 

    """
    def __init__(self, source_path, cdescontroller, sample_rows, maxlevels):

        sourcedb = CsvDB('hospitaldb', [source_path], schematype='source')
        # get the cde dataset name
        self.__target_dbname = cdescontroller.cdedataset_name
        # use it also as filename by adding .csv extension
        self.__target_filename = self.__target_dbname + '.csv'
        # use as target folder the mipqctool/data/mapping/target
        # this will be used in the mapping execution by mipmap engine
        self.__target_folder = os.path.join(str(PARENTPATH), 'data',
                                            'mapping', 'target')
        self.__target_path = os.path.join(self.__target_folder,
                                          self.__target_filename)
        # create a csv file with the cde headers only
        cdescontroller.save_csv_headers_only(self.__target_path)
        # now we can create the CsvDB for the target schema
        targetdb = CsvDB(self.__target_dbname,
                         [self.__target_path],
                         schematype='target')
        # create the Mapping object
        self.__mapping = Mapping(sourcedb, targetdb)
        # store the QcSchema for the cde datset
        self.__cde_schema = cdescontroller.dataset_schema
        # With QcTable we can access medata about the source csv
        self.__srctbl = QcTable(source_path, schema=None)
        # inder the table schema
        self.__srctbl.infer(limit=sample_rows, maxlevels=maxlevels)
        self.__src_path = source_path
        self.__src_folder = os.path.dirname(source_path)
        # create table report for the source file
        self.__tblreport = TableReport(self.__srctbl)
        self.__src_filename = self.__srctbl.filename
        self.__src_headers = self.__srctbl.headers4mipmap
        # get the cde headers
        self.__cde_headers = cdescontroller.cde_headers
        self.__cde_mapped = self.__mapping.correspondences.keys()
        self.__cde_not_mapped = self.__cde_headers
        # get source vars for each cde correspondence
        self.__cde_corrs_sources = []

    @property
    def sourcereport(self):
        return self.__tblreport

    @property
    def source_filename(self):
        return self.__src_filename

    @property
    def source_headers(self):
        return self.__src_headers

    @property
    def corr_sources(self):
        return self.__cde_corrs_sources

    @property
    def cde_filename(self):
        return self.__target_filename

    @property
    def cde_mapped(self):
        return self.__cde_mapped

    @property
    def cde_not_mapped(self):
        return self.__cde_not_mapped

    def suggest_corr(self, cdedict, threshold):
        """
        Arguments:
        :param cdedict: CdeDict object
        :param threshold: 0-1 similarity threshold, below that not a cde is suggested
        """
        cde_sugg_dict = {}
        source_table = self.__srctbl.filename
        target_table = self.__target_filename
        #source_raw_headers = self.__mapping.sourcedb.get_raw_table_headers(source_table)
        for name, columnreport in self.__tblreport.columnreports.items():
            cde = cdedict.suggest_cde(columnreport, threshold=threshold)
            # check if a cde mapping already exist
            if cde and cde.code not in cde_sugg_dict.keys():
                cde_sugg_dict[cde.code] = self.__mapping.sourcedb.raw_2_mipmap_header(
                    self.__src_filename,
                    columnreport.name
                )
        for cde, source_var in cde_sugg_dict.items():
            source_paths = [(source_table, source_var, None)]
            target_path = (target_table, cde, None)
            expression = '.'.join([os.path.splitext(source_table)[0], source_var])
            try:
                self.__mapping.add_corr(source_paths=source_paths, target_path=target_path,
                                        expression=expression)
            # If a cde correspondance already exists then pass
            except MappingError:
                pass
        self.__update_cde_mapped()

    def add_corr(self, cde, source_cols, expression):
        source_paths = [(self.__srctbl.filename, col, None) for col in source_cols]
        target_path = (self.__target_filename, cde, None)
        self.__mapping.add_corr(source_paths, target_path, expression)
        self.__update_cde_mapped()

    def remove_corr(self, cde):
        self.__mapping.remove_corr(cde)
        self.__update_cde_mapped()

    def update_corr(self, cde, source_cols, expression):
        source_paths = [(self.__srctbl.filename, col, None) for col in source_cols]
        target_path = (self.__target_filename, cde, None)
        self.__mapping.update_corr(source_paths, target_path, expression)
        self.__update_cde_mapped()

    def get_corr_expression(self, cde):
        return self.__mapping.correspondences[cde].expression

    def get_col_stats(self, mipmap_column) -> dict:
        """returns source columns stats.
        Arguments:
        :param mipmap_column: mipmap tranformed column name
        """
        stats = {}
        raw_headers =  self.__mapping.sourcedb.get_raw_table_headers(self.source_filename)
        # convert the column that is mipmap formated to the initial column name
        col = raw_headers[mipmap_column]
        col_report = self.__tblreport.columnreports[col]
        if col_report:
            stats['miptype'] = col_report.miptype
            stats['value_range'] = col_report.value_range
            return stats
        else:
            return None

    def get_cde_info(self, mipmap_cde) -> dict:
        """returns cde type and values.
        Arguments:
        :param mipmap_cde: mipmap tranformed cde name
        """
        cde_info = {}
        raw_cde_dict = self.__mapping.targetdb.get_raw_table_headers(self.cde_filename)
        raw_cde = raw_cde_dict[mipmap_cde]
        cde_schema = self.__cde_schema
        cdefield = cde_schema.get_field(raw_cde)
        cde_type = cdefield.miptype
        constraints = cdefield.constraints
        if cde_type == 'nominal' and constraints:
            con = constraints.get('enum')
        elif cde_type in ['numerical', 'integer'] and constraints:
            con = [constraints.get('minimum'), constraints.get('maximum')]
        else:
            con = None

        cde_info = {'miptype': cde_type, 'constraints': con}
        return cde_info
        

    def get_source_raw_header(self, mipmap_col):
        raw_headers =  self.__mapping.sourcedb.get_raw_table_headers(self.source_filename)
        return raw_headers[mipmap_col]

    def get_cde_raw_header(self, mipmap_col):
        raw_headers = self.__mapping.targetdb.get_raw_table_headers(self.__target_filename)
        return raw_headers[mipmap_col]

    def get_cde_mipmap_header(self, raw_cde_header):
        raw_headers = self.__mapping.targetdb.get_raw_table_headers(self.__target_filename)
        mipmap_headers = {value:key for key, value in raw_headers.items()}
        return mipmap_headers[raw_cde_header]

    def run_mapping(self, output):
        xml_folder = os.path.join(str(PARENTPATH), 'data',
                                  'mapping', 'xml')
        xml_path = os.path.join(xml_folder, 'map.xml')
        with open(xml_path, 'w') as mapxml:
            mapxml.write(self.__mapping.xml_string)
        DockerMipmap(xml_folder, self.__src_folder, self.__target_folder, output)

    def replace_function(self, column, replacments):
        """Returns a mipmap function string with encapsulated if statements 
        for replacing given values of a column with predefined ones. 
        This is used in a categorical/nominal column type

        Arguments:
        :param columnname: the column name(str)
        :param repls: list with Replacement namedtuples
                    Replacement('source', 'target')   
        """
        return ifstr(column, replacments)

            
       

    def __update_cde_mapped(self):
        self.__cde_mapped = list(self.__mapping.correspondences.keys())
        cde_not_mapped = self.__cde_headers.copy()
        cde_corrs_sources = OrderedDict()
        for cde in self.__cde_mapped:
            cde_not_mapped.remove(cde)
            source_paths = self.__mapping.correspondences[cde].source_paths
            pathstring = ','.join([path[1] for path in source_paths])
            cde_corrs_sources[cde] = pathstring

        self.__cde_corrs_sources = cde_corrs_sources
        self.__cde_not_mapped = cde_not_mapped
