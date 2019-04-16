# -*- coding: utf-8 -*-
# sequence.py

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

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
        # free memory
        # TODO: investigate if there is a need to keep
        self.__validdicoms = []

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
            if len(set(values)) != 1:
                self.__errortags.append(seqtag)
        self.__data = data

    def validate(self):
        # invalid dicom validation
        if len(self.__invaliddicoms) > 0:
            self.__errors.append('contains invalid dicom files')
        # resolution validation
        pixelspacing = self.data['PixelSpacing']
        zspacing = self.data['SliceThickness']
        if pixelspacing != 'Tag not found' and zspacing != 'Tag not found':
            pixelspacing = ast.literal_eval(pixelspacing)
            self.__px_X = float(pixelspacing[0])
            self.__px_Y = float(pixelspacing[1])
            self.__px_Z = float(zspacing)
            if self.__px_X >= 1.5 or self.__px_Y >= 1.5:
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
            if 'T1' in protocol:
                self.__protocol = 'T1'
            else:
                self.__errors.append('not a T1 image')
        else:
            self.__errors.append('SeriesDescription tag is missing')
        # number of slices validation
        if self.slices < 40:
            self.__errors.append('minimum number of slices failure')

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
