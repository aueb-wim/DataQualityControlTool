# -*- coding: utf-8 -*-
# config.py

from __future__ import division
from __future__ import print_function
from __future__ import absolute_import
from __future__ import unicode_literals

import logging
import sys

# Create logger
LOGGER = logging.getLogger('qctool')
LOGGER.setLevel(logging.DEBUG)
C_HANDLER = logging.StreamHandler(sys.stdout)
C_FORMAT = logging.Formatter('%(name)s: %(levelname)s: %(message)s')
C_HANDLER.setFormatter(C_FORMAT)
LOGGER.addHandler(C_HANDLER)


def debug(debug_on=True):
    """Turn debugging of qctool on or off.
    Sets the logger level to debug
    """
    global LOGGER, DEBUGGING
    if debug_on:
        LOGGER.setLevel(logging.DEBUG)
        DEBUGGING = True
    else:
        LOGGER.setLevel(logging.WARNING)
        DEBUGGING = False


# force level=Warning
debug(False)

# Global constants
ERROR = 'qctool.error'
REMOTE_SCHEMES = ['http', 'https', 'ftp', 'ftps']
DEFAULT_MISSING_VALUES = ['']
PANDAS_NANS = ['', '#N/A', '#N/A N/A', '#NA', '-1.#IND',
                   '-1.#QNAN', '-NaN', '-nan', '1.#IND', '1.#QNAN',
                   'N/A', 'NA', 'NULL', 'NaN', 'n/a', 'nan', 'null']

# Dicom constants
ID_TAGS = ['PatientID', 'StudyID', 'SeriesNumber', 'InstanceNumber']
DATE_TAGS = ['AcquisitionDate', 'SeriesDate', 'PatientAge', 'PatientBirthDate']
REQUIRED_TAGS = ['PatientID', 'StudyID', 'SeriesDescription',
                 'SeriesNumber', 'InstanceNumber', 'ImagePosition',
                 'ImageOrientation', 'SliceLocation', 'SamplesPerPixel',
                 'Rows', 'Columns', 'PixelSpacing', 'BitsAllocated',
                 'BitsStored', 'HighBit']
ONEOFTWO_TAGS = [('AcquisitionDate', 'SeriesDate'),
                 ('PatientAge', 'PatientBirthDate')]
OPTIONAL_TAGS = ['MagneticFieldStrength', 'PatientSex', 'Manufacturer',
                 'ManufacturerModelName', 'InstitutionName', 'StudyDescription',
                 'SliceThickness', 'RepetitionTime', 'EchoTime',
                 'SpacingBetweenSlices', 'NumberOfPhaseEncodingSteps',
                 'EchoTrainLength', 'PercentPhaseFieldOfView',
                 'PixelBandwidth', 'FlipAngle', 'PercentSampling',
                 'EchoNumbers']
SEQUENCE_TAGS = ['PatientID', 'StudyID', 'SeriesDescription',
                 'SeriesNumber', 'ImageOrientation',  'SamplesPerPixel',
                 'Rows', 'Columns', 'PixelSpacing', 'BitsAllocated',
                 'BitsStored', 'HighBit', 'AcquisitionDate', 'SeriesDate',
                 'PatientAge', 'PatientBirthDate', 'MagneticFieldStrength',
                 'PatientSex', 'Manufacturer',
                 'ManufacturerModelName', 'InstitutionName', 'StudyDescription',
                 'SliceThickness', 'RepetitionTime', 'EchoTime',
                 'SpacingBetweenSlices', 'NumberOfPhaseEncodingSteps',
                 'EchoTrainLength', 'PercentPhaseFieldOfView',
                 'PixelBandwidth', 'FlipAngle', 'PercentSampling',
                 'EchoNumbers']
ALL_TAGS = REQUIRED_TAGS + DATE_TAGS + OPTIONAL_TAGS
