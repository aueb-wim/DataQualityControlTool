
import os
from mipqctool.model.qcfrictionless import QcTable, FrictionlessFromDC

class DataDB(object):
    def __init__(self, dbname, tables, dbtype='csv'):
        """"
        Arguements: 
        :param dbname: tha name of the database
        :param tables: list of QcTable objects
        :param type: 'csv' or 'reletional'
        """
        self.__dbname = dbname
        self.__type = dbtype
        # store QcTable objects in a dictionary with filename as key
        self.__tables = {table.filename: table for table in tables}
        # dublications
        self.__dublications = {table.filename: 0 for table in tables}

    @property
    def totaltables(self):
        return len(self.__tables)

    def get_table_headers(self, name) -> list:
        """
        Returns the headers of table given its name.
        Arguments:
        :param name: string with the filename of the table
                     in the case where the table corresponds to 
                     a csv file 
        """
        table = self.__tables.get(name)
        if table:
            return table.actual_headers
        else:
            return None

    def columnforxml(self, name, column, dublication=None) -> str:
        """
        Return a column name for mipmap xml correspondence element.
        Arguments:
        :param name: the name of the table (filename for csv table)
        :param column: the header name of the table 
        :param dublication: integer, number of dublicaton of the table, 
                            if it is used in the correpondence
        """
        basename = os.path.splitext(name)[0]
        if dublication:
            dublic = '_' + str(dublication) + '_'
            return '.'.join([self.__dbname, basename + dublic, basename + 'Tuple', column])
        else:
            return '.'.join([self.__dbname, basename, basename + 'Tuple', column])

    @classmethod
    def from_csvs(cls, dbname, filepaths):
        """
        Constructs a DataDB object given a list with csv filepaths.
        """
        tables = [QcTable(fpath, schema=None) for fpath in filepaths]
        return cls(dbname=dbname, tables=tables)
