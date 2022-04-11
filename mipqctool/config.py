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
DEBUG_HANDLER = logging.FileHandler('debug.log')
DEBUG_HANDLER.setLevel(level=logging.DEBUG)
INFO_HANDLER = logging.StreamHandler(sys.stdout)
INFO_HANDLER.setLevel(level=logging.INFO)

C_FORMAT = logging.Formatter('%(asctime)s: %(name)s: %(levelname)s: %(message)s')
INFO_HANDLER.setFormatter(C_FORMAT)
DEBUG_HANDLER.setFormatter(C_FORMAT)

LOGGER.addHandler(INFO_HANDLER)
LOGGER.addHandler(DEBUG_HANDLER)

DEBUGGING = False


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
DC_DOMAIN = 'http://datacatalogue.hbpmip.link:4200'
DC_SUBDOMAIN_ALLPATHOLOGIES = '/pathology/allPathologies'

MIPMAP_DB_CONTAINER = 'mipmap_postgres'
MIPMAP_DB_NAME = 'mipmap'
MIPMAP_DB_PORT = 5433
MIPMAP_DB_USER = 'mipmap'
MIPMAP_DB_PASSWORD = 'mipmap'

ERROR = 'qctool.error'
REMOTE_SCHEMES = ['http', 'https', 'ftp', 'ftps']


DEFAULT_MISSING_VALUES = ['']
DEFAULT_QCFIELD_MIPTYPE = 'text'
DEFAULT_QCFIELD_CONCEPTPATH = ''
DEFAULT_QCFIELD_METHODOLOGY = ''

DEFAULT_DATE_FORMAT = '%Y-%m-%d'
PANDAS_NANS = ['', '#N/A', '#N/A N/A', '#NA', '-1.#IND',
                   '-1.#QNAN', '-NaN', '-nan', '1.#IND', '1.#QNAN',
                   'N/A', 'NA', 'NULL', 'NaN', 'n/a', 'nan', 'null']

# Data Catalogue 
DC_HEADERS = [
    'csvFile', 'name', 'code', 'type', 'values',
    'unit', 'description', 'comments', 'conceptPath',
    'methodology', 'canBeNull'
    ]

DC_TYPES = ['real', 'integer', 'nominal', 'ordinal', 'date', 'text']
DC_DATE_FORMAT = '%Y-%m-%d'

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


# lookup tables
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
        'outliers': 'Total number of outliers',
        'upperbound': 'Outlier upper bound',
        'lowerbound': 'Outlier lower bound',
        'outliersrows': 'Rows with outliers',
        'std': 'Standard deviation',
        'max': 'Maximum value',
        'min': 'Minimum value',
        'bottom5': '5 least frequent values',
        'top5': '5 most frequent values'}

COLUMN_STAT_HEADERS = [
    'mean',
    'std',
    'max', 
    'min',
    'mode',
    'q1',  
    'median',
    'q3',
    'categories', 
    'categories_num',
    'unique',
    'top',                      
    'outliers',
    'upperbound', 
    'lowerbound', 
    'outliersrows', 
    'bottom5', 
    'top5',
]


SQL_KEYWORDS = {
    "ADD", 	
    "ALL",		
    "ALTER",  	
    "AND",
    "ANY",
    "AS",
    "ASC",
    "BACKUP",
    "BETWEEN",
    "BY",	
    "CASE", 	
    "CHECK", 	
    "COLUMN", 
    "CONSTRAINT", 	
    "CREATE", 	
    "DATABASE",
    "DEFAULT", 	
    "DELETE",	
    "DESC",
    "DISTINCT",
    "DROP",
    "EXEC",
    "EXISTS",
    "FOREIGN",
    "FROM",	
    "FULL",
    "JOIN",
    "GROUP",
    "HAVING",
    "IN",
    "INDEX",
    "INNER",
    "INSERT", 
    "INT",
    "INTO",
    "IS",
    "LEFT",
    "LIKE",	
    "LIMIT",	
    "NOT",	
    "NULL",	
    "OR",
    "ORDER",
    "OUTER",
    "PRIMARY",
    "KEY",
    "PROCEDURE",
    "REPLACE",
    "RIGHT",
    "ROWNUM",
    "SELECT",	
    "TOP",	
    "SET",
    "TABLE",
    "TRUNCATE",
    "UNION",
    "ALL",
    "UNIQUE",	
    "UPDATE",
    "VALUES",
    "VIEW",	
    "WHERE",
    "ASCII",
    "CHAR_LENGTH",	
    "CHARACTER_LENGTH", 	
    "CONCAT", 
    "CONCAT_WS", 	
    "FIELD",
    "FIND_IN_SET",
    "FORMAT",
    "INSTR", 	
    "LCASE",
    "LENGTH",	
    "LOCATE",
    "LOWER",
    "LPAD",
    "LTRIM",
    "MID",
    "POSITION",
    "REPEAT",
    "REVERSE",
    "RPAD",
    "RTRIM",
    "SPACE",
    "SUBSTR",
    "SUBSTRING",
    "SUBSTRING_INDEX",
    "TRIM",
    "UCASE",
    "UPPER",
    "ABS",
    "ACOS",
    "ASIN",
    "ATAN",
    "ATAN2",
    "AVG",
    "CEIL",
    "CEILING",
    "COS",
    "COT",
    "COUNT",
    "DEGREES",
    "DIV",
    "EXP",
    "FLOOR",
    "GREATEST",
    "LEAST",
    "LN",
    "LOG",
    "LOG10",
    "LOG2",
    "MAX",
    "MIN",
    "MOD",
    "PI",
    "POW",
    "POWER",
    "RADIANS",
    "RAND",
    "ROUND",
    "SIGN",
    "SIN",
    "SQRT",
    "SUM",
    "TAN",
    "TRUNCATE",
    "ADDDATE",
    "ADDTIME,"
    "CURDATE",
    "CURRENT_DATE",
    "CURRENT_TIME",
    "CURRENT_TIMESTAMP",
    "CURTIME",
    "DATE",
    "DATEDIFF",
    "DATE_ADD",
    "DATE_FORMAT",
    "DATE_SUB",
    "DAY",
    "DAYNAME",
    "DAYOFMONTH",
    "DAYOFWEEK",
    "DAYOFYEAR",
    "FROM_DAYS",
    "HOUR",
    "LAST_DAY",
    "LOCALTIME",
    "LOCALTIMESTAMP",
    "MAKEDATE",
    "MAKETIME",
    "MICROSECOND",
    "MINUTE",
    "MONTH",
    "MONTHNAME",
    "NOW",
    "PERIOD_ADD",
    "PERIOD_DIFF",
    "QUARTER",
    "SECOND",
    "SEC_TO_TIME",
    "STR_TO_DATE",
    "SUBDATE",
    "SUBTIME",
    "SYSDATE",
    "TIME",
    "TIME_FORMAT",
    "TIME_TO_SEC",
    "TIMEDIFF",
    "TIMESTAMP",
    "TO_DAYS",
    "WEEK",
    "WEEKDAY",
    "WEEKOFYEAR",
    "YEAR",
    "YEARWEEK",
    "BIN",
    "BINARY",
    "CASE",
    "CAST",
    "COALESCE",
    "CONNECTION_ID",
    "CONV",
    "CONVERT",
    "CURRENT_USER",
    "IF",
    "IFNULL",
    "ISNULL",
    "LAST_INSERT_ID",
    "NULLIF",
    "SESSION_USER",
    "SYSTEM_USER",
    "USER",
    "VERSION",
}