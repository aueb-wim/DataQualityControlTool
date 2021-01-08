import csv

import pandas as pd

from mipqctool.config import LOGGER, DC_HEADERS


class QCtoDC(object):
    """Class for transforming a frictionless json to Data Catalogue format
    """

    def __init__(self, qcdescriptor, csvname=None, cde_suggestions=None):
        self.__qctodcvars = []
        if cde_suggestions:
            self.__suggestions = cde_suggestions
        else:
            self.__suggestions = {}
        for qcdesc in qcdescriptor['fields']:
            name = qcdesc['name']
            cde_suggestion = self.__suggestions.get(name, [None, name])
            cde = cde_suggestion[0]
            conceptpath = cde_suggestion[1]
            qc2dcvar = QctoDCVariable(qcdesc, csvname, conceptpath, cde)
            self.__qctodcvars.append(qc2dcvar)

    def export2csv(self, filepath):
        with open(filepath, 'w') as csvfile:
            headers = DC_HEADERS
            writer = csv.DictWriter(csvfile, fieldnames=headers)
            writer.writeheader()
            for dcvar in self.__qctodcvars:
                writer.writerow(dcvar.info)

    def export2excel(self, filepath):
        d={}
        for h in DC_HEADERS:
            d[h] = [v.info[h] for v in self.__qctodcvars]
        df = pd.DataFrame.from_dict(d)
        df = df[DC_HEADERS]
        df.to_excel(filepath, index=False)

class QctoDCVariable(object):
    """Class for transorming a qcfield to a DC variable"""

    def __init__(self, qcdescriptor, csvname, concepthpath, cde=None):
        self.__csvname = csvname
        self.__miptype = qcdescriptor.get('MIPType', 'text')
        self.__type = self.__get_dc_type()
        self.__sqltype = qcdescriptor.get('type')
        self.__code = qcdescriptor.get('name')
        self.__name = qcdescriptor.get('title', self.__code)
        self.__desc = qcdescriptor.get('description')
        self.__format = qcdescriptor.get('format', 'default')
        self.__constraints = qcdescriptor.get('constraints')
        self.__conceptpath = concepthpath
        self.__cde = cde
        if self.__constraints:
            self.__values = self.__get_values()
        else:
            self.__values = None

    @property
    def info(self):
        d = {
            'csvFile': self.__csvname,
            'name': self.__name,
            'code': self.__code,
            'type': self.__type,
            'values': self.__values,
            'unit': '',
            'canBeNull': 'Y',
            'description': self.__desc,
            'comments': '',
            'conceptPath': self.__conceptpath,
            'methodology': '',
            'sql_type': self.__sqltype,
            'cde': self.__cde
        }
        return d

    def __get_values(self):
        if self.__type == 'nominal':
            enum = self.__constraints.get('enum', [])
            val = ['{{"{}","{}"}}'.format(v, v) for v in enum]
            return ','.join(val)
        elif self.__type == 'ordinal':
            enum = self.__constraints.get('enum', [])
            val = ['{{"{}","{}"}}'.format(v, order) for order,v in enumerate(enum, start=1)]
            return ','.join(val)
        elif self.__type in ['integer', 'real']:
            minimum = self.__constraints.get('minimum')
            minimum = str(minimum)
            maximum = self.__constraints.get('maximum')
            maximum = str(maximum)
            if minimum != 'None' and maximum != 'None':
                return '-'.join([minimum, maximum])

    def __get_dc_type(self):
        if self.__miptype =='numerical':
            return 'real'
        else:
            return self.__miptype
