# qctable.py

from tableschema import Table
from collections import defaultdict

class QcTable(Table):
    def __init__(self, source, **kargs):
        self.__data = defaultdict(list)
        self.__columns = None
        super().__init__(source, **kargs)
        for row in super().read(keyed=True):
            for k, v in row.items():
                self.__data[k].append(v)

    @property
    def data(self):
        return self.__data
    