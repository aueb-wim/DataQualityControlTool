import re
from openpyxl import load_workbook

from mipqctool.config import SQL_KEYWORDS, ERROR
from mipqctool.model.qctypes.numerical import infer_numerical

class DcExcel(object):
    """Class for validating a Data Catalogues excel file."""
    def __init__(self, filepath):
        self.__variables = {}
        self.__conncept_paths = []
        self.__doublicates_cpaths = {}
        self.__invalid_enums = {}
        wb = load_workbook(filepath)
        ws = wb.active
        for row in ws.iter_rows(min_row=1, max_row=1):
            headers =  [cell.value.lower() for cell in row]
        for row in ws.iter_rows(min_row=2):
            values = [cell.value for cell in row]
            metadata = dict(zip(headers, values))
            code = metadata['code']
            mip_type = metadata['type']
            mip_values = metadata['values']
            conceptpath = metadata['conceptpath']
            if conceptpath not in self.__conncept_paths:
                self.__conncept_paths.append(conceptpath)
            else:
                self.__doublicates_cpaths[code] = conceptpath

            excelvar = ExcelVariable(code, mip_type, mip_values, conceptpath)
            if excelvar.invalid_enums:
                self.__invalid_enums[code] = excelvar.invalid_enums

            self.__variables[code] = excelvar


    @property
    def variables(self) -> dict:
        """Dict with variable data"""
        return self.__variables

    @property
    def invalid_enums(self) -> dict:
        return self.__invalid_enums

    @property
    def doubl_conceptpaths(self) -> dict:
        return self.__doublicates_cpaths

    @property
    def is_valid(self):
        if (len(self.__doublicates_cpaths) + len( self.__invalid_enums)) == 0:
            return True
        else:
            return False


class ExcelVariable(object):
    """Class for validating a DC variable from excel file."""
    def __init__(self, code, cdetype, values, conceptpath):
        """
        Arguments:
        :param code: string with the variable code
        :param cdetype: string with the mip type
        :param values: string with the variable values
        :param concepthpath: string with the conceptpath of the variable
        """
        self.__enum_regx = '{(?P<list>[^\{]*)}'
        self.__code = code
        self.__type = cdetype
        self.__strvalues = values
        self.__concepthpath = conceptpath
        self.__invalid_enums = []
        self.__validate()

    @property
    def code(self):
        return self.__code

    @property
    def type(self):
        return self.__type

    @property
    def concepthpath(self):
        return self.__concepthpath

    @property
    def invalid_enums(self):
        return self.__invalid_enums

    def __validate(self):
        if self.__type == 'nominal':
            enumerations = self.__tolist_enums(self.__strvalues)
            for enum in enumerations:
                if self.__is_valid_enum(enum):
                    continue
                else:
                    self.__invalid_enums.append(enum)

    def __tolist_enums(self, enumstr) -> set:
        all_enums= []
        matches = re.findall(self.__enum_regx, enumstr)
        for m in matches:
            items = re.findall(r'"[^"]*"', m)
            for item in items:
                # remove double quates
                without_quotes = item.replace('\"','')
                # remove left and right spaces from each enum and convert to lowercase
                all_enums.append(without_quotes.upper().strip())
        return set(all_enums)

    def __is_valid_enum(self, value):
        if value in SQL_KEYWORDS:
            return False
        # try to find if the string represents a numerical value with or without suffix
        elif infer_numerical(value) != ERROR:
            return False
        else:
            return True




