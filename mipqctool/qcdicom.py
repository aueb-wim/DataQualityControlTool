# qcdicom.py
import datetime
import os
import pydicom
import pandas as pd
from . import __version__

# Default dicom metadata requirements file
# DEFAULT_REQ = 'data/dicom_metadata_req.csv'


def get_requirements(filename):
    """Return a pandas df with the dicom metatata requierements"""
    return pd.read_csv(filename)


def getsubfolders(rootfolder):
    """Returns dict with keys subfolders and values a list
    of the containing dcm files in each folder"""
    dirtree = os.walk(rootfolder)
    result = {}
    for root, dirs, files in dirtree:
        del dirs  # Not used
        # Get all the visible subfolders
        for name in files:
            if name.endswith('.dcm'):
                subfolder, filename = removeroot(os.path.join(root, name),
                                                 rootfolder)
                if subfolder in result.keys():
                    result[subfolder].append(filename)
                else:
                    result[subfolder] = [filename]
    return result


def removeroot(filepath, rootfolder):
    """Removes the root path from a given filepath."""
    subfolder = os.path.dirname(os.path.relpath(filepath, rootfolder))
    filename = os.path.basename(filepath)
    return (subfolder, filename)

class DicomReport(object):
    """A class for producing a metadata report of
    a dataset of DICOM images
    """
    def __init__(self, rootfolder, username):
        """ Arguments:
            :param rootfolder: folder path with DICOMs subfolders
            :param dicomreq: pandas df with dicom metadata requirements
            :param username: str with the username
            """
        self.mandatory = None
        self.oneof = None
        self.optional = None
        self.dicoms = pd.DataFrame()
        self.reportdata = None
        self.rootfolder = rootfolder
        self.subfolders = getsubfolders(rootfolder)
        self.username = username
        self.readicoms()

    def _set_requirements(self, df):
        mand = df[df['mandatory'] == 'Yes']
        self.mandatory = mand['tag'].tolist()
        opt = df[df['mandatory'] == 'No']
        self.optional = opt['tag'].tolist()
        oneof = df[~df['mandatory'].isin(['Yes', 'No'])]
        oneof_dict = {}
        for index, row in oneof.iterrows():
            del index  # not used
            if row['mandatory'] not in oneof_dict.keys():
                oneof_dict[row['mandatory']] = []
            oneof_dict[row['mandatory']].append(row['tag'])
        self.oneof = oneof_dict

    def _read_dicom(self, filename, subfolder):
        """Read dicom headers except PixelData, returns a dataframe"""
        filepath = os.path.join(self.rootfolder, subfolder, filename)
        ds = pydicom.dcmread(filepath)
        columns = ds.dir()
        data = {}
        data['folder'] = subfolder
        data['file'] = filename
        for tag in columns:
            if tag != 'PixelData' and not tag.endswith('Sequence'):
                data[tag] = [ds.data_element(tag).value]
#                except AttributeError:
#                    data[tag] = 'Error! Value not found!'
        dicomdf = pd.DataFrame.from_dict(data)
        return dicomdf

    def readicoms(self):
        dataset = {'version': [__version__],
                   'date_qc_ran': [datetime.datetime.now()],
                   'username': [self.username],
                   'dicom_folder': [os.path.abspath(self.rootfolder)]}
        self.dataset = pd.DataFrame.from_dict(dataset)
        for folder in self.subfolders:
            for dicom in self.subfolders[folder]:
                dicomdf = self._read_dicom(dicom, folder)
                with open('dicom_qctool.log', 'a') as f:
                    dicomdf[['folder', 'file']].to_csv(f, header=False, index=False)
                self.dicoms = pd.concat([self.dicoms, dicomdf],
                                        ignore_index=True)
        self.dicoms.set_index(['folder', 'file'], inplace=True)

    def export2xls(self, filepath):
        """Export the report in excel file"""
        writer = pd.ExcelWriter(filepath)
        self.dataset.to_excel(writer, sheet_name='general_info',
                              index=False)
        self.dicoms.to_excel(writer, sheet_name='dicom_metadata')
        writer.save()
