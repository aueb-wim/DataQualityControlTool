# sequence.py
import ast
import collections
from . import config
from .config import LOGGER

config.debug(True)


class MRISequence(object):
    def __init__(self, patientid, studyid, seriesnum, dicoms):
        self.__studyid = studyid
        self.__patientid = patientid
        self.__snumber = seriesnum
        self.__errortags = []
        self.__validdicoms = []
        self.__invaliddicoms = []
        self.__errors = []
        self.__px_X = None
        self.__px_Y = None
        self.__px_Z = None
        self.__isisometric = False
        self.__isisotropic = False
        self.__protocol = None
        self.__data = None
        self.__slices = len(dicoms)
        self.__validate_dicoms(dicoms)
        self.__getseqdata()
        self.validate()

    @property
    def studyid(self):
        return self.__studyid

    @property
    def patientid(self):
        return self.__patientid

    @property
    def seriesnumber(self):
        return self.__snumber

    @property
    def seriesdate(self):
        return self.__data.get('SeriesDate')

    @property
    def seriesdescription(self):
        return self.__data.get('SeriesDescription', 'No SeriesDescription')

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
        return self.__slices

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
    def invaliddicoms(self):
        return self.__invaliddicoms

    @property
    def dicoms(self):
        return self.__validdicoms

    @property
    def info(self):
        info = collections.OrderedDict()
        info['PatientID'] = self.patientid
        info['StudyId'] = self.studyid
        info['SeriesNumber'] = self.seriesnumber
        info['Slices'] = self.slices
        info['SeriesDescription'] = self.__data.get('SeriesDescription',
                                                    'No SeriesDescription')
        info['SeriesDate'] = self.seriesdate
        return info

    @property
    def errordata(self):
        errordata = collections.OrderedDict()
        errordata['PatientID'] = self.__patientid
        errordata['StudyID'] = self.__studyid
        errordata['SeriesNumber'] = self.__snumber
        errordata['Slices'] = self.slices
        errordata['Invalid_dicoms'] = len(self.__invaliddicoms)
        errordata['SeriesDescription'] = self.__data.get('SeriesDescription',
                                                         'No SeriesDescription')

        for i in range(6):
            keyerror = 'Error_%i' % (i+1)
            try:
                errordata[keyerror] = self.__errors[i]
            except IndexError:
                errordata[keyerror] = None
        return errordata

    def validate(self):
        # invalid dicom validation
        if len(self.__invaliddicoms) > 0:
            self.__errors.append('contains invalid dicom files')
        # resolution validation
        max_res = config.MAX_RESOLUTION
        pixelspacing = self.data['PixelSpacing']
        zspacing = self.data['SliceThickness']
        if pixelspacing != 'Tag not found' and zspacing != 'Tag not found':
            pixelspacing = ast.literal_eval(pixelspacing)
            self.__px_X = float(pixelspacing[0])
            self.__px_Y = float(pixelspacing[1])
            self.__px_Z = float(zspacing)
            if self.__px_X >= max_res or self.__px_Y >= max_res:
                self.__errors.append('maximum resolution failure')
            if self.__px_X == self.__px_Y:
                self.__isisometric = True
                if self.__px_X == self.__px_Z:
                    self.__isisotropic = True
        else:
            self.__errors.append('resolution tags are missing')
        # protocol validation
        protocol = self.data['SeriesDescription']
        if protocol != 'Tag not found':
            for scan_type in config.SCAN_TYPES:
                if scan_type in protocol:
                    self.__protocol = scan_type
                else:
                    error_message = 'not a {} scan type'.format(scan_type)
                    self.__errors.append(error_message)
        else:
            self.__errors.append('SeriesDescription tag is missing')
        # number of slices validation
        if self.slices < config.MIN_SLICES:
            self.__errors.append('minimum number of slices failure')

    # Private

    def __validate_dicoms(self, dicoms):
        for dicom in dicoms:
            if dicom.isvalid:
                self.__validdicoms.append(dicom)
            else:
                self.__invaliddicoms.append(dicom)

    def __getseqdata(self):
        data = collections.OrderedDict()
        dicoms = self.__validdicoms
        # case of sequence with only invalid dicom files
        # get sequence data from them
        if len(self.__validdicoms) == 0 and len(self.__invaliddicoms) > 0:
            dicoms = self.__invaliddicoms

        for seqtag in config.SEQUENCE_TAGS:
            values = list(d.data[seqtag] for d in dicoms)
            # get the most frequent element
            data[seqtag] = max(set(values), key=values.count)
            # store the tag that has more than one values anyway
            # in errortags, not used at the moment somewhere
            if len(set(values)) != 1:
                self.__errortags.append(seqtag)
        self.__data = data
