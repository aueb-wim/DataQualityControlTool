import requests
import json

from mipqctool.config import LOGGER


class DcConnector(object):
    """This class gets cde json data from Data Cataloge web API.

    Arguemnts:
    :param dcrequest: request object from DC api returning all 
                      pathologies metadata
    """

    __pnames = []
    __versions = []
    __all_json = None
    __status_code = None

    def __init__(self, dcrequest):
        all_json = dcrequest.json()
        # did we have a success respond from server?
        if dcrequest.status_code == 200:
            # get all pathologies names in a list
            self.__pnames = [t['name'] for t in all_json]
            # get all avalable versions per pathology in a dictionary
            self.__versions = {t['name']: [v['name'] for v in t['versions']] for t in all_json}
            # store all the data in a dictionary
            self.__all_json = all_json

        self.__status_code = dcrequest.status_code

    def getjson(self, pathology, version):
        p_index = self.__pnames.index(pathology)
        v_index = self.__versions[pathology].index(version)
        str_json = self.__all_json[p_index]['versions'][v_index]['jsonString']
        return json.loads(str_json)

    def get_pathology_versions(self, pathology):
        return self.__versions[pathology]

    @property
    def status_code(self):
        return self.__status_code

    @property
    def pathology_names(self):
        return self.__pnames
