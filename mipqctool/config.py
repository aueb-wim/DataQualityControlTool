# config.py

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
REMOTE_SCHEMES = ['http', 'https', 'ftp', 'ftps']

# Dicom constants

ID_TAGS = ['PatientID', 'StudyID', 'SeriesNumber', 'InstanceNumber']
DATE_TAGS = ['AcquisitionDate', 'SeriesDate', 'StudyDate', 'PatientAge',
             'PatientBirthDate']

# START of section for MIP requirments
REQUIRED_TAGS = ['PatientID', 'StudyID', 'SeriesDescription',
                 'SeriesNumber', 'InstanceNumber',
                 'SliceLocation', 'SamplesPerPixel',
                 'Rows', 'Columns', 'PixelSpacing', 'BitsAllocated',
                 'BitsStored', 'HighBit']

ONEOFTWO_TAGS = [('AcquisitionDate', 'SeriesDate'),
                 ('PatientAge', 'PatientBirthDate'),
                 ('ImageOrientation', 'ImageOrientationPatient'),
                 ('ImagePosition', 'ImagePositionPatient')]
# ImageOrientation and ImagePosition are retired from DICOM standard
# and replaced eith ImageOrientationPatient and ImagePositionPatient
# we put them in the above list for backward compatibility

MAX_RESOLUTION = 1.5
MIN_SLICES = 40
SCAN_TYPES = ['T1']

# END of section for  MIP requirments

OPTIONAL_TAGS = ['MagneticFieldStrength', 'PatientSex', 'Manufacturer',
                 'ManufacturerModelName', 'InstitutionName',
                 'StudyDescription',
                 'SliceThickness', 'RepetitionTime', 'EchoTime',
                 'SpacingBetweenSlices', 'NumberOfPhaseEncodingSteps',
                 'EchoTrainLength', 'PercentPhaseFieldOfView',
                 'PixelBandwidth', 'FlipAngle', 'PercentSampling',
                 'EchoNumbers', 'StudyDate',
                 'ImagePosition', 'ImagePositionPatient',
                 'ImageOrientation', 'ImageOrientationPatient']

SEQUENCE_TAGS = ['PatientID', 'StudyID', 'SeriesDescription',
                 'SeriesNumber', 'ImageOrientation', 'ImageOrientationPatient',
                 'SamplesPerPixel',
                 'Rows', 'Columns', 'PixelSpacing', 'BitsAllocated',
                 'BitsStored', 'HighBit', 'AcquisitionDate', 'SeriesDate',
                 'PatientAge', 'PatientBirthDate', 'MagneticFieldStrength',
                 'PatientSex', 'Manufacturer',
                 'ManufacturerModelName', 'InstitutionName',
                 'StudyDescription',
                 'SliceThickness', 'RepetitionTime', 'EchoTime',
                 'SpacingBetweenSlices', 'NumberOfPhaseEncodingSteps',
                 'EchoTrainLength', 'PercentPhaseFieldOfView',
                 'PixelBandwidth', 'FlipAngle', 'PercentSampling',
                 'EchoNumbers']

ALL_TAGS = REQUIRED_TAGS + DATE_TAGS + OPTIONAL_TAGS
