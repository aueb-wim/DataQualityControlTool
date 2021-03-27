
from mipqctool.model.mapping import Mapping, CsvDB
from mipqctool.model.qcfrictionless import CdeDict
from mipqctool.controller import CDEsController

class MipCDEMapper(object):
    """Class for handling a simple (one to one) mapping task 
    and creating  the mapping xml for mipmap engine. 
    
    :Arguments:
    :source path: the filepath of the source csv
    :cdecontroller: a CDEsController object
    :param cdedict: a CdeDict object for suggesting

    """
    def __init__(self, source_path, cdecontroller, cdedict=None):
        pass