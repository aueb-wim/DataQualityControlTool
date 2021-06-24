import os
from xml.etree.ElementTree import Element
from mipqctool.exceptions import MappingValidationError
from mipqctool.config import LOGGER

class Correspondence(object):
    """Class for storing and processing a mapping correpondence.
    Arguments:
    :param mapping: A Mapping object
    :param source_paths: list of tuples (table_name, column_name, dublication)
                         dublication number could be used in future development
                         if there is no duplication then use None as third element
    :param target_path:  tuple with the CDE table and name variable and dublication
    :param expression:   string with expression given by the user, the paths are given
                         in this string as <table>.<column>
    :param replacements: list with Replacement named tupples for the case here we have a nominal
                         values.This doesn't play any role in tha mapping xml, stores info about the
                         replacements for GUI display perposes. 
    """
    def __init__(self, mapping, source_paths, target_path, expression, replacements=None):
        self.__mapping = mapping
        self.__source_paths = source_paths  # list of source variables
        self.__target_path = target_path  # the target CDE

        self.__expression = expression
        self.__replacements = replacements
        self.__validate_tables()
        self.__xml_element = None
        self.__create_xml_element()

        # need to validate tha expression
        # self.firstSyntaxCheck()
        # then produce the xml valid expression

    @property
    def source_paths(self) -> list:
        return self.__source_paths

    @property
    def sourcepaths_str(self) -> str:
        return ','.join(['.'.join([os.path.splitext(srcpath[0])[0], srcpath[1]]) for srcpath in self.source_paths])
        
    @property
    def targetpath_str(self) -> str:
        return '.'.join(self.__target_path)
        

    @property
    def target_path(self) -> tuple:
        return self.__target_path

    @property
    def expression(self) -> str:
        """The """
        return self.__expression

    @property
    def replacements(self) -> list:
        """List with Replacement named tupples"""
        return self.__replacements

    @property
    def xml_element(self):
        return self.__xml_element

    def __validate_tables(self):
        sourcedb = self.__mapping.sourcedb
        targetdb = self.__mapping.targetdb

        cde_table, cde, cde_dublication = self.__target_path

        # check source tables and headers
        for table, column, dublication in self.__source_paths:
            source_headers = sourcedb.get_table_headers(table)
            if source_headers:
                if column not in source_headers:
                    msg = '{} column not found in {} table.'.format(column, table)
                    raise MappingValidationError(msg)
                if dublication and dublication > sourcedb.get_table_dublicates(table):
                    msg = 'Dublication number "{}" of table {} exceeds the declared dublications'.format(dublication, table)
                    raise MappingValidationError(msg)
            else:
                msg = '{} table not found in the {} database'.format(table, sourcedb.name)
                raise MappingValidationError(msg)

        # check target tables and headers
        target_headers = targetdb.get_table_headers(cde_table)
        if target_headers:
            if cde not in target_headers:
                msg = '{} cde variable not found in {} cde table.'.format(cde, cde_table)
                raise MappingValidationError(msg)
            if cde_dublication and cde_dublication > targetdb.get_table_dublicates(cde_table):
                msg = 'Dublication number "{}" of table {} exceeds the declared dublications'.format(cde_dublication, cde_table)
                raise MappingValidationError(msg)
        else:
            msg = '{} cde table not found in {} database.'.format(cde_table, targetdb.name)
            raise MappingValidationError(msg)

    def __create_xml_element(self):
        expression = self.__expression
        sourcedb = self.__mapping.sourcedb
        targetdb = self.__mapping.targetdb
        main_element = Element('correspondence')
        sources_element = Element('source-paths')
        for table, column, duplication in self.__source_paths:
            basename = os.path.splitext(table)[0]
            tobereplaced = '.'.join([basename, column])
            xmlcolumn = sourcedb.columnforxml(table, column, duplication)
            expression = expression.replace(tobereplaced, xmlcolumn)
            src_element = Element('source-path')
            src_element.text = xmlcolumn
            sources_element.append(src_element)
        target_element = Element('target-path')
        cdexmlcolumn = targetdb.columnforxml(*self.__target_path)
        basecdefile = os.path.splitext(self.__target_path[0])[0]
        cdecolumn = self.__target_path[1]
        cde2bereplaced = '.'.join([basecdefile, cdecolumn])
        expression = expression.replace(cde2bereplaced, cdexmlcolumn)
        target_element.text = cdexmlcolumn
        tranformfunc_element = Element('transformation-function')
        tranformfunc_element.text = expression
        confidence_element = Element('confidence')
        confidence_element.text = '1.0'
        subelements = [sources_element, target_element, tranformfunc_element, confidence_element]
        main_element.extend(subelements)
        self.__xml_element = main_element

   