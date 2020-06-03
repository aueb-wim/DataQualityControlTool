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
DEFAULT_QCFIELD_MIPTYPE = 'text'
DEFAULT_DATE_FORMAT = '%Y-%m-%d'
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


#lookup tables
PRETTY_STAT_NAMES = {
        'categories': 'List of category values',
        'categories_num': 'Number of categories',
        'unique': 'Count of unique values (for text variables)',
        'top': 'Most frequent value',
        'mode': 'Mode (most frequent value)',
        'freq': 'Number of occurrences for most frequent value',
        'q1': ('25% of records are below this value'
                '(limit value of the first quartile)'),
        'median': '50% of records are below this value (median)',
        'q3': ('75% of records are below this value'
               '(limit value of the third quartile)'),
        'outliers': 'Total number of outliers (outside 3 std.dev)',
        'upperbound': 'Outlier upper bound',
        'lowerbound': 'Outlier lower bound',
        'outliersrows': 'Rows with outliers',
        'std': 'Standard deviation',
        'max': 'Maximum value',
        'min': 'Minimum value',
        'bottom5': '5 least frequent values',
        'top5': '5 most frequent values'}
