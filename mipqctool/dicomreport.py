# -*- coding: utf-8 -*-
# dicomreport.py

from __future__ import division
from __future__ import print_function
from __future__ import absolute_import
from __future__ import unicode_literals

import datetime
import os
import json
import csv
import multiprocessing as mp
from multiprocessing import Pool
import pydicom
import pandas as pd
from .config import LOGGER
from .qcdicom import Qcdicom
from .sequence import Sequence
from . import config, __version__

DIR_PATH = os.path.dirname(os.path.realpath(__file__))
config.debug(True)

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
    def __init__(self, rootfolder, username):
        """ Arguments:
            :param rootfolder: folder path with DICOMs subfolders
            :param dicomreq: pandas df with dicom metadata requirements
            :param username: str with the username
            """
        self.reportdata = None
        self.rootfolder = rootfolder
        self.subfolders = getsubfolders(rootfolder)
        self.username = username
        self.dataset = {'version': [__version__],
                        'date_qc_ran': [datetime.datetime.now()],
                        'username': [username],
                        'dicom_folder': [os.path.abspath(rootfolder)]}
        self.__notprocessed = []
        self.__invalidseq = []
        self.__validseq = []
        self.readicoms_parallel(mp.cpu_count() + 1)
        LOGGER.info('Good seq: %i' % len(self.__validseq))
        LOGGER.info('Bad seq: %i' % len(self.__invalidseq))
        LOGGER.info('Files not processed %i' % len(self.__notprocessed))

    def readicoms_parallel(self, processes):
        """Read all the dicoms using multiprocessing."""
        output = []
        if len(self.subfolders) > processes:
            LOGGER.info('dicom parallel processing with {} Processes'.format(processes))
            slices = list(splitdict(self.subfolders, processes))
            with Pool(processes) as p:
                output = p.map(self.readicoms_chunks, slices)
        else:
            LOGGER.info('Single core processing...')
            output = self.readicoms_chunks(self.subfolders)
        for chunk in output:
            self.__validseq += chunk['validseq']
            self.__invalidseq += chunk['invalidseq']
            self.__notprocessed += chunk['notprocessed']

    def __validseq2csv(self, filepath):
        with open(filepath, 'w') as csvfile:
            fieldnames = list(self.__validseq[0].data.keys())
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            for seq in self.__validseq:
                writer.writerow(seq.errordata)

    def __invalidseq2csv(self, filepath1, filepath2):
        with open(filepath1, 'w') as csvfile:
            fieldnames = list(self.__invalidseq[0].errordata.keys())
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            append = False
            fields = None
            for seq in self.__invalidseq:
                writer.writerow(seq.errordata)
                if len(seq.invaliddicoms) > 0:
                    fields = self.__invaliddicoms2csv(filepath2,
                                                      seq.invaliddicoms,
                                                      append=append,
                                                      fields=fields)
                    append = True


    def __invaliddicoms2csv(self, filepath, dicoms, append=False, fields=None):
        fieldnames = fields
        if append:
            with open(filepath, 'a') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                for dicom in dicoms:
                    writer.writerow(dicom.errordata)
        else:
            with open(filepath, 'w') as csvfile:
                fieldnames = list(dicoms[0].errordata.keys())
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                for dicom in dicoms:
                    writer.writerow(dicom.errordata)
        return fieldnames

    def __notproc2csv(self, filepath):
        with open(filepath, 'w') as csvfile:
            fieldnames = ['Folder', 'File']
            writer = csv.writer(csvfile)
            writer.writerow(fieldnames)
            for nodcmfile in self.__notprocessed:
                writer.writerow(nodcmfile)

    def writereport(self, folderpath):
        directory = folderpath
        vseqfilepath = os.path.join(directory, 'validsequences.csv')
        invseqfilepath = os.path.join(directory, 'invalidsequences.csv')
        invdicomfilepath = os.path.join(directory, 'invaliddicoms.csv')
        notprocfilepath = os.path.join(directory, 'notprocessed.csv')
        if len(self.__validseq) > 0:
            self.__validseq2csv(vseqfilepath)
        if len(self.__invalidseq) > 0:
            self.__invalidseq2csv(invseqfilepath, invdicomfilepath)
        if len(self.__notprocessed) > 0:
            self.__notproc2csv(notprocfilepath)

    def readicoms_chunks(self, filesdict):
        result = {
                 'validseq': [],
                 'invalidseq': [],
                 'notprocessed': []
                 }
        for folder in filesdict:
            output = self.__getsequences(folder, filesdict[folder])
            for k in result.keys():
                result[k] = result[k] + output[k]
        return result

    def __getsequences(self, folder, dicomfiles):
        dicoms = {}
        result = {
                 'validseq': [],
                 'invalidseq': [],
                 'notprocessed': []
                 }
        for filename in dicomfiles:
            try:
                qcdcm = Qcdicom(filename, folder, self.rootfolder)
                id3 = (qcdcm.patientid, qcdcm.studyid, qcdcm.seqnumber)
                if id3 in dicoms.keys():
                    dicoms[id3].append(qcdcm)
                else:
                    dicoms[id3] = [qcdcm]

            except pydicom.errors.InvalidDicomError:
                result['notprocessed'].append((folder, filename))

        for id3 in dicoms.keys():
            newseq = Sequence(id3[0], id3[1], id3[2], dicoms[id3])
            if newseq.isvalid:
                result['validseq'].append(newseq)
            else:
                result['invalidseq'].append(newseq)
        return result

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
