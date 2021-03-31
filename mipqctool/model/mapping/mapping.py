from collections import OrderedDict
from xml.etree.ElementTree import Element
import xml.etree.ElementTree
from xml.dom import minidom

from mipqctool.model.mapping import Correspondence
from mipqctool.exceptions import MappingError
class Mapping(object):
    """Class for creating a mapping task xml for mipmap engine.
    This Class works for the case we have just one csv file as target db. 
    The corrispondences are stored in a dict with the target column (cde in this case)
    as a key. Cases that we have multiple files in target or dublications, or joined tables 
    are not covered. 
    
    Arguments:
    :param sourcedb: DataDB object 
    :param targetdv: DataDB object
    """
    def __init__(self, sourcedb, targetdb):
        self.__source = sourcedb
        self.__target = targetdb
        self.__correspondences = OrderedDict() # Dict: key:CDE code ->Value: correspondence

    @property
    def sourcedb(self):
        return self.__source

    @property
    def targetdb(self):
        return self.__target

    @property
    def xml_string(self):
        data = self.__create_xml()
        initial_str = xml.etree.ElementTree.tostring(data)
        return minidom.parseString(initial_str).toprettyxml(indent="   ")


    def add_correspondence(self, source_paths, target_path, expression):
        """
        Arguments:
        :source_paths: list of tuples (table_name, column_name, dublication)
                   dublication number could be used in future development
                   if there is no duplication then use None as third element
        :target_path:  tuple with the CDE table and name variable and dublication
        :expression:   string with expression given by the user, the paths are given
                       in this string as <table>.<column>
        """
        corr = Correspondence(self, source_paths, target_path, expression)
        cde_name = target_path[1]
        if cde_name in self.__correspondences.keys():
            msg = 'There is a mapping correspondance for {} cde. Delete it first to proceed.'
            raise MappingError(msg)
        else:
            self.__correspondences[cde_name] = corr

    def del_correspondence(self, cde_name):
        self.__correspondences.pop(cde_name, None) #throughs KeyError exception

    # examines if there already exists a correspondence for this CDE
    def contains(self, code) -> bool:
        return code in self.__correspondences.keys()

    def __create_xml(self):
        map_element = Element('mappingtask')
        config_element = Element('config')

        conf_1 = Element('rewriteSubsumptions')
        conf_1.text = 'true'
        conf_2 = Element('rewriteCoverages')
        conf_2.text = 'true'
        conf_3 = Element('rewriteSelfJoins')
        conf_3.text = 'true'
        conf_4 = Element('rewriteEGDs')
        conf_4.text = 'false'
        conf_5 = Element('sortStrategy')
        conf_5.text = '-1'
        conf_6 = Element('skolemTableStrategy')
        conf_6.text = '-1'
        conf_7 = Element('useLocalSkolem')
        conf_7.text = 'false'

        config_element.extend([
            conf_1,
            conf_2,
            conf_3,
            conf_4,
            conf_5,
            conf_6,
            conf_7
        ])

        source_elem = Element('source')
        source_elem.extend(self.sourcedb.xml_elements)

        target_elem = Element('target')
        
        target_elem.extend(self.targetdb.xml_elements)

        corrspons_elem = Element('correspondences')
        corrs_elements = [corr.xml_element for corr in self.__correspondences.values()]
        corrspons_elem.extend(corrs_elements)

        map_element.extend([config_element, source_elem, target_elem, corrspons_elem])
        return map_element
   
