# sequence.py
import ast
import collections
from . import config
from .config import LOGGER

config.debug(True)


class Sequence(object):
    def __init__(self, patientid, studyid, seriesnum, dicoms):
        self.__studyid = studyid
        self.__patientid = patientid
        self.__snumber = seriesnum    
        self.__dicoms = dicoms
        self.__errortags = []
        self.__errors = []
        self.__px_X = None
        self.__px_Y = None
        self.__px_Z = None
        self.__isisometric = False
        self.__isisotropic = False
        self.__protocol = None
        self.__data = None

        self.__getseqdata()
        self.validate()


    def __getseqdata(self):
        data = collections.OrderedDict()
        for seqtag in config.SEQUENCE_TAGS:
            values = list(d.data[seqtag] for d in self.__dicoms)
            # get the most frequent element
            data[seqtag] = max(set(values), key=values.count)
            if len(set(values)) != 1:
                self.__errortags.append(seqtag)
        self.__data = data

    def __getresolution(self):
        pixelspacing = self.data['PixelSpacing']
        pixelspacing = ast.literal_eval(pixelspacing)
        self.__px_X = float(pixelspacing[0])
        self.__px_Y = float(pixelspacing[1])
        self.__px_Z = float(self.data['SliceThickness'])
        if self.__px_X == self.__px_Y:
            self.__isisometric = True
            if self.__px_X == self.__px_Z:
                self.__isisotropic = True
        self.__data['Slices'] = self.slices
        self.__data['isisotropic'] = self.isotropic
        self.__data['isisometric'] = self.ismetric

    def __getprotocol(self):
        protocol = self.data['SeriesDescription']
        if 'T1' in protocol:
            self.__protocol = 'T1'

    def validate(self):
        self.__getresolution()
        self.__getprotocol()
        if self.__px_X >= 1.5 or self.__px_Y >= 1.5:
            self.__errors.append('maximum resolution failure')
        if self.slices < 40:
            self.__errors.append('minimum number of slices failure')
        if self.__protocol != 'T1':
            self.__errors.append('not a T1 image')

    @property
    def studyid(self):
        return self.__studyid

    @property
    def patientid(self):
        return self.__patientid

    @property
    def seriesnum(self):
        return self.__snumber

    @property
    def pixelspacingX(self):
        return self.__px_X

    @property
    def pixelspacingY(self):
        return self.__px_Y

    @property
    def data(self):
        return self.__data

    @property
    def slices(self):
        return len(self.__dicoms)

    @property
    def isotropic(self):
        return self.__isisotropic

    @property
    def ismetric(self):
        return self.__isisometric

    @property
    def isvalid(self):
        if len(self.__errors) == 0:
            return True
        else:
            return False

    @property
    def errordata(self):
        errordata = collections.OrderedDict()
        errordata['PatientID'] = self.__patientid
        errordata['StudyID'] = self.__studyid
        errordata['SeriesNumber'] = self.__snumber
        errordata['Slices'] = self.slices
        errordata['SeriesDescription'] = self.__data['SeriesDescription']

        for i in range(6):
            keyerror = 'Error_%i' % (i+1)
            try:
                errordata[keyerror] = self.__errors[i]
            except IndexError:
                errordata[keyerror] = None
        return errordata
