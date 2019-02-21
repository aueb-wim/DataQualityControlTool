# qcdicom.py
import datetime
import os
import json
import sys
import logging
import multiprocessing as mp
from multiprocessing import Pool
import pydicom
import pandas as pd
from . import __version__

DIR_PATH = os.path.dirname(os.path.realpath(__file__))

# Create logger
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.DEBUG)

# Create hadlers to the logger
C_HANDLER = logging.StreamHandler(sys.stdout)
C_HANDLER.setLevel(logging.DEBUG)

# Create formatters and add it to the hadler
C_FORMAT = logging.Formatter('%(name)s: %(levelname)s: %(message)s')
C_HANDLER.setFormatter(C_FORMAT)

# Add haldlers to the logger
LOGGER.addHandler(C_HANDLER)


def getsubfolders(rootfolder):
    """Returns dict with keys subfolders and values a list
    of the containing dcm files in each folder"""
    dirtree = os.walk(rootfolder)
    result = {}
    for root, dirs, files in dirtree:
        del dirs  # Not used
        # Get all the visible subfolders
        for name in files:
            subfolder, filename = removeroot(os.path.join(root, name),
                                             rootfolder)
            if subfolder in result.keys():
                result[subfolder].append(filename)
            else:
                result[subfolder] = [filename]
    return result


def getsubfolders2list(rootfolder):
    """Returns dict with keys subfolders and values a list
    of the containing dcm files in each folder"""
    dirtree = os.walk(rootfolder)
    subfolders = set()
    result = []
    for root, dirs, files in dirtree:
        del dirs  # Not used
        # Get all the visible subfolders
        for name in files:
            subfolder, filename = removeroot(os.path.join(root, name),
                                             rootfolder)
            if subfolder in subfolders:
                result.append([subfolder, filename])
            else:
                result[subfolder] = [filename]
    return result


def removeroot(filepath, rootfolder):
    """Removes the root path from a given filepath."""
    subfolder = os.path.dirname(os.path.relpath(filepath, rootfolder))
    filename = os.path.basename(filepath)
    return (subfolder, filename)


def splitdict(bigdict, n):
    """Split a dictionary to n parts."""
    chunksize = len(bigdict) / float(n)
    for i in range(n):
        start = int(round(i * chunksize))
        end = int(round((i + 1) * chunksize))
        yield dict(list(bigdict.items())[start:end])


class DicomReport(object):
    """A class for producing a metadata report of
    a dataset of DICOM images
    """
    def __init__(self, rootfolder, username, dicom_schema):
        """ Arguments:
            :param rootfolder: folder path with DICOMs subfolders
            :param dicomreq: pandas df with dicom metadata requirements
            :param username: str with the username
            """
        self.mandatory = []
        self.oneof = None
        self.optional = None
        self.dicoms = pd.DataFrame()
        self.reportdata = None
        self.rootfolder = rootfolder
        self.subfolders = getsubfolders(rootfolder)
        self.username = username
        self.get_dicom_schema(dicom_schema)
        self.dataset = {'version': [__version__],
                        'date_qc_ran': [datetime.datetime.now()],
                        'username': [username],
                        'dicom_folder': [os.path.abspath(rootfolder)]}
        self.readicoms_parallel(mp.cpu_count() + 1)
#        self.readicoms()

    def get_dicom_schema(self, schemafile):
        with open(schemafile, 'r', encoding='UTF8') as read_file:
            dicom_schema = json.load(read_file)
        for field in dicom_schema['fields']:
            self.mandatory.append(field['name'])

    def _read_dicom(self, filename, subfolder):
        """Read dicom headers except PixelData, returns a dataframe"""
        filepath = os.path.join(self.rootfolder, subfolder, filename)
        # Read the dcm file but not the PixelData
        try:
            columns = self.mandatory
            ds = pydicom.dcmread(filepath, 
                                 stop_before_pixels=True,
                                 specific_tags=columns)
            data = {}
            data['folder'] = subfolder
            data['file'] = filename
            for tag in columns:
                # Don't tags that represent sequence
                # Sequence tags are big strings and contain commas
                # that corrupt the exported csv file
                # if not tag.endswith('Sequence'):
                try:
                    data[tag] = [str(ds.data_element(tag).value)]
                except AttributeError:
                    LOGGER.info('For %s the type is %s', tag, type(ds.data_element(tag)))
                    data[tag] = ['Error! Value not found!']
                except KeyError:
                    data[tag] = ['Tag not found']
            dicomdf = pd.DataFrame.from_dict(data)
            return dicomdf
        except pydicom.errors.InvalidDicomError:
            raise pydicom.errors.InvalidDicomError

    def readicoms_parallel(self, processes):
        """Read all the dicoms using multiprocessing."""
        if len(self.subfolders) > processes:
            print('dicom parallel processing with {} Processes'.format(processes))
            slices = list(splitdict(self.subfolders, processes))
            dcms = []
            with Pool(processes) as p:
                dcms = p.map(self.readicoms_chunks, slices)
            self.dicoms = pd.concat(dcms, ignore_index=True)
            self.dicoms.set_index(['folder', 'file'], inplace=True)
        else:
            print('Single core processing...')
            self.readicoms()

    def readicoms(self):
        self.dicoms = self.readicoms_chunks(self.subfolders)
        self.dicoms.set_index(['folder', 'file'], inplace=True)

    def readicoms_chunks(self, filesdict):
        """Read the given dicoms and return a df."""
        dcms = []
        for folder in filesdict:
            for dicom in filesdict[folder]:
                try:
                    with open('qctool_dicom_files_read.log', 'a') as f:
                        f.write(folder + ',' + dicom + '\n')
                    dcms.append(self._read_dicom(dicom, folder))
                except pydicom.errors.InvalidDicomError:
                    continue
        return pd.concat(dcms, ignore_index=True)

    def export2xls(self, filepath):
        """Export the report in excel file"""
        writer = pd.ExcelWriter(filepath)
        dataset_df = pd.DataFrame.from_dict(self.dataset)
        dataset_df.to_excel(writer, sheet_name='general_info',
                            index=False)
        # save to csv first
        self.dicoms.to_csv(filepath[:-4] + '.csv')
        # split the dicoms headers into chunks of 65530 rows
        # 2007 excel files can handle max 65536 rows
        maxsize = 65530
        dicoms_size = len(self.dicoms)
        if dicoms_size < maxsize:
            self.dicoms.to_excel(writer, sheet_name='dicom_metadata')
        else:
            chunk = 0
            for i in range(0, dicoms_size, maxsize):
                chunk += 1
                self.dicoms.iloc[i:i + maxsize, :].to_excel(writer,
                    sheet_name='dicom_matadata_part{0}'.format(chunk))
        writer.save()
