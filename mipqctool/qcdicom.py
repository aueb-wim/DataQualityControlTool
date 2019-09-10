# qcdicom.py
import datetime
import os
import json
import collections
import multiprocessing as mp
from multiprocessing import Pool
import pydicom
import pandas as pd
from .config import LOGGER
from . import config, __version__

DIR_PATH = os.path.dirname(os.path.realpath(__file__))
config.debug(True)


class Qcdicom(object):
    """A class for storing dicom headers
    """
    def __init__(self, filename, folder, rootfolder):

        # Set attributes
        # ordered dict for storing header values
        self.__data = collections.OrderedDict()
        self.__instnumber = None # instance number
        self.__studyid = None #  mri studyid from header
        self.__patientid = None # patient ID from header
        self.__snumber = None # Series number from header
        self.__pydicom = None # a pydicom.dataset object
        self.__folder = folder
        self.__file = filename
        self.__missingtags = set()
        self.__errors = []
        self.filepath = os.path.join(rootfolder, folder, filename)

        # load the dcm file
        try:
            self.__pydicom = pydicom.dcmread(self.filepath,
                                             stop_before_pixels=True)
            self.__findmissingtags()
            self.__getids()
            self.__getdata()

        except pydicom.errors.InvalidDicomError:
            message = '%s is not a dicom file' % self.__file
            raise pydicom.errors.InvalidDicomError(message)

    def __findmissingtags(self):
        for tag in config.REQUIRED_TAGS:
            if tag not in self.__pydicom.dir():
                self.__missingtags.add(tag)
        # check if the one of the two tags exist in the file
        for tags in config.ONEOFTWO_TAGS:
            oneoftwo = 0
            for tag in tags:
                if tag in self.__pydicom.dir():
                    oneoftwo = 1
                # if both are not present add them to missing tags
                if oneoftwo == 0:
                    for tag in tags:
                        self.__missingtags.add(tag)

    def __getdata(self):
        for tag in config.ALL_TAGS:
            try:
                self.__data[tag] = str(self.__pydicom.data_element(tag).value)
            except KeyError:
                self.__data[tag] = 'Tag not found'

    def __getids(self):
        ids = set(config.ID_TAGS)
        # id tags are not missing
        if not ids.intersection(self.__missingtags):
            self.__patientid = self.__pydicom.data_element('PatientID').value
            self.__studyid = self.__pydicom.data_element('StudyID').value
            self.__snumber = self.__pydicom.data_element('SeriesNumber').value
            self.__instnumber = int(self.__pydicom.data_element('InstanceNumber').value)

    def validate(self):
        self.__findmissingtags()

    def modify_patient_name(self, new_name):
        self.__pydicom.PatientsName = new_name
        self.__pydicom.save_as(self.filepath)

    @property
    def studyid(self):
        return self.__studyid

    @property
    def patientid(self):
        return self.__patientid

    @property
    def seqnumber(self):
        return self.__snumber

    @property
    def instancenum(self):
        return self.__instnumber

    @property
    def isvalid(self):
        if len(self.__missingtags) == 0:
            return True
        else:
            return False

    @property
    def missingtags(self):
        return [tag for tag in self.__missingtags]

    @property
    def folder(self):
        return self.__folder

    @property
    def filename(self):
        return self.__file

    @property
    def data(self):
        return self.__data

    @property
    def errordata(self):
        errordata = collections.OrderedDict()
        errordata['Folder'] = self.__folder
        errordata['File'] = self.__file
        errordata['PatientID'] = self.__data['PatientID']
        errordata['StudyID'] = self.__data['StudyID']
        errordata['SeriesNumber'] = self.__data['SeriesNumber']
        errordata['InstanceNumber'] = self.__data['InstanceNumber']
        errordata['MissingTags'] = ','.join(self.missingtags)
        return errordata

