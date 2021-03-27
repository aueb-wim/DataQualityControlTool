
import os
from xml.etree.ElementTree import Element
from mipqctool.model.qcfrictionless import QcTable
from mipqctool.exceptions import MappingValidationError

class CsvDB(object):
    def __init__(self, dbname, filepaths, schematype='source'):
        """"
        Arguements: 
        :param dbname: tha name of the database
        :param tables: list of QcTable objects
        :param schematype: 'source' or 'target'
        """
        self.__dbname = dbname
        self.__dbtype = 'CSV'
        self.__schematype = schematype

        tables = [QcTable(fpath, schema=None) for fpath in filepaths]
  
        # store QcTable objects in a dictionary with filename as key
        self.__tables = {table.filename: table for table in tables}
        # dublications
        self.__dublications = {} #{table.filename: int}
        self.__xml_elements = None
        self.__create_xml_element()

    
    @property
    def name(self):
        return self.__dbname
        
    @property
    def totaltables(self):
        return len(self.__tables)

    @property
    def dbtype(self):
        return self.__dbtype

    @property
    def xml_elements(self):
        return self.__xml_elements

    def get_table_dublicates(self, name) -> int:
        "Returns how many dublicates a given table has."
        return self.__dublications.get(name)

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
        #headers = self.get_table_headers(name)
        #if headers:
        #    if column not in headers:
        #        msg = "There is no '{}' column in '{}' table.".format(column, name)
        #        raise MappingValidationError(msg)
        #else:
        #    msg = "'{} table not found in the '{}' database.".format(name, self.__dbname)
        #    raise MappingValidationError(msg)
        basename = os.path.splitext(name)[0]
        if dublication:
            dublic = '_' + str(dublication) + '_'
            return '.'.join([self.__dbname, basename + dublic, basename + 'Tuple', column])
        else:
            return '.'.join([self.__dbname, basename, basename + 'Tuple', column])
    
    def __create_xml_element(self):

        type_elem = Element('type')
        type_elem.text = 'CSV'

        csv_elem = Element('csv')

        csvdbname_elem = Element('csv-db-name')
        csvdbname_elem.text = self.name

        tables_elem = Element('csv-tables')

        for qctable in self.__tables.values():
            table_elem = Element('csv-table')
            schema_elem = Element('schema')
            if self.__schematype == 'source':
                schema_elem.text = 'source/' + qctable.filename
            else:
                schema_elem.text = 'target/' + qctable.filename
            instances_elem = Element('instances')
            
            # build instance xml elemnent
            instance_elem = Element('instance')
            path_elem = Element('path')
            if self.__schematype == 'source':
                path_elem.text = 'source/' + qctable.filename
            else:
                path_elem.text = 'target/' + qctable.filename
            column_names_elem = Element('column-names')
            column_names_elem.text = 'true'
            instance_elem.extend([path_elem, column_names_elem])

            instances_elem.append(instance_elem)
            table_elem.extend([schema_elem, instances_elem])

            # append the current table element to the tables xml element
            tables_elem.append(table_elem)

        csv_elem.extend([csvdbname_elem, tables_elem])
        
        xml_elements = [type_elem, csv_elem]
        xml_elements.append(Element('inclusions'))
        xml_elements.append(Element('exclusions'))
        xml_elements.append(Element('duplications'))
        xml_elements.append(Element('functionalDependencies'))
        xml_elements.append(Element('selectionConditions'))
        xml_elements.append(Element('joinConditions'))
        self.__xml_elements = xml_elements

