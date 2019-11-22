# dicomreport.py
import datetime
import os
import shutil
import json
import csv
import multiprocessing as mp
from multiprocessing import Pool
import pydicom
import pandas as pd
from .config import LOGGER
from .mridicom import MRIDicom
from .mrisequence import MRISequence
from .mristudy import MRIStudy
from .mripatient import MRIPatient
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
        self.__patients = []
        self.__totalvalidseq = 0
        self.__totalstudies = 0

        # Read all the dcm files and calc QC stats
        self.__readicoms_parallel(mp.cpu_count() + 1)

        for patient in self.__patients:
            self.__totalstudies += len(patient.studies)
            for study in patient.studies:
                self.__totalvalidseq += len(study.sequences)

        LOGGER.info('Patients with good seq: %i' % self.totalpatients)
        LOGGER.info('Total visits: %i' % self.totalvisits)
        LOGGER.info('Good seq: %i' % self.totalvalidsequences)
        LOGGER.info('Bad seq: %i' % self.totalinvalidsequences)
        LOGGER.info('Files not processed %i' % self.totalbadfiles)

    def __readicoms_parallel(self, processes):
        """Read all the dicoms using multiprocessing."""
        output = []
        if len(self.subfolders) > processes:
            LOGGER.info('dicom parallel processing with {} Processes'.format(processes))
            slices = list(splitdict(self.subfolders, processes))
            with Pool(processes) as p:
                output = p.map(self.readicoms_chunks, slices)
            for chunk in output:
                self.__patients += chunk['patients']
                self.__invalidseq += chunk['invalidseq']
                self.__notprocessed += chunk['notprocessed']
        else:
            LOGGER.info('Single core processing...')
            output = self.readicoms_chunks(self.subfolders)
            self.__patients += output['patients']
            self.__invalidseq += output['invalidseq']
            self.__notprocessed += output['notprocessed']

    def __validseq2csv(self, filepath):
        with open(filepath, 'w') as csvfile:
            # a sequence object just to take the correct header names
            asequence = self.__patients[0].studies[0].sequences[0]
            fieldnames = list(asequence.info.keys())
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            for patient in self.__patients:
                for study in patient.studies:
                    for seq in study.sequences:
                        writer.writerow(seq.info)

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
        if os.path.isfile(vseqfilepath):
            os.remove(vseqfilepath)
        invseqfilepath = os.path.join(directory, 'invalidsequences.csv')
        if os.path.isfile(invseqfilepath):
            os.remove(invseqfilepath)
        invdicomfilepath = os.path.join(directory, 'invaliddicoms.csv')
        if os.path.isfile(invdicomfilepath):
            os.remove(invdicomfilepath)
        notprocfilepath = os.path.join(directory, 'notprocessed.csv')
        if os.path.isfile(notprocfilepath):
            os.remove(notprocfilepath)
        if len(self.__patients) > 0:
            self.__validseq2csv(vseqfilepath)
        else:
            open(vseqfilepath, 'w').close()
        if len(self.__invalidseq) > 0:
            self.__invalidseq2csv(invseqfilepath, invdicomfilepath)
            if not os.path.isfile(invdicomfilepath):
                open(invdicomfilepath, 'w').close()
        else:
            open(invseqfilepath, 'w').close()
            open(invdicomfilepath, 'w').close()
        if len(self.__notprocessed) > 0:
            self.__notproc2csv(notprocfilepath)
        else:
            open(notprocfilepath, 'w').close()

    def reorganizefiles(self, output):
        """reorganize the dcm files in a folder structure for
        LORIS import pipeline.
        Arguments:
        :param output: output folder
        """
        LOGGER.info('Reorganizing files for LORIS pipeline into folder: %s' % output)
        for patient in self.patients:
            patientid = patient.patientid
            patdir = os.path.join(output, patientid)
            if not os.path.exists(patdir):
                os.mkdir(patdir)
            study_count = 0
            for study in patient.studies:
                study_count += 1
                d = [patientid, str(study_count)]
                studydir = os.path.join(patdir, '_'.join(d))
                if not os.path.exists(studydir):
                    os.mkdir(studydir)
                for seq in study.sequences:
                    for dicom in seq.dicoms:
                        sourcepath = dicom.filepath
                        destpath = os.path.join(studydir, dicom.filename)
                        shutil.copy(sourcepath, destpath)

    def readicoms_chunks(self, filesdict):
        result = {
                 'patients': [],
                 'invalidseq': [],
                 'notprocessed': []
                 }
        for folder in filesdict:
            output = self.__getsequences(folder, filesdict[folder])
            for k in result.keys():
                result[k] = result[k] + output[k]
        return result

    def __getsequences(self, folder, dicomfiles):
        # dicts for storing list of objects grouped by the
        #  a given key
        sequence_ids = {}
        study_ids = {}
        patient_ids = {}
        result = {
                 'patients': [],
                 'invalidseq': [],
                 'notprocessed': []
                 }
        # read each dcm file and find in which sequence belongs to
        # by collecting the sequence keys patientid, stydyid, seqnumber
        for filename in dicomfiles:
            try:
                qcdcm = MRIDicom(filename, folder, self.rootfolder)
                id3 = (qcdcm.patientid, qcdcm.studyid, qcdcm.seqnumber)
                if id3 in sequence_ids.keys():
                    sequence_ids[id3].append(qcdcm)
                else:
                    sequence_ids[id3] = [qcdcm]
            # the file is dcm but something is wrong with the file
            except pydicom.errors.InvalidDicomError:
                result['notprocessed'].append((folder, filename))

        for id3 in sequence_ids.keys():
            id2 = (id3[0], id3[1])
            newseq = MRISequence(id3[0], id3[1], id3[2], sequence_ids[id3])
            # perform the MIP validation for the sequence
            if newseq.isvalid:
                # put it in a list grouped by the study id
                # and patient id
                if id2 in study_ids.keys():
                    study_ids[id2].append(newseq)
                else:
                    study_ids[id2] = [newseq]
            else:
                result['invalidseq'].append(newseq)

        for id2 in study_ids.keys():
            patientid, studyid = id2
            newstudy = MRIStudy(patientid, studyid, study_ids[id2])
            if patientid in patient_ids.keys():
                patient_ids[patientid].append(newstudy)
            else:
                patient_ids[patientid] = [newstudy]

        for pid in patient_ids.keys():
            newpatient = MRIPatient(pid, patient_ids[pid])
            result['patients'].append(newpatient)

        return result

    @property
    def patients(self):
        return self.__patients

    @property
    def totalpatients(self):
        return len(self.__patients)

    @property
    def totalvisits(self):
        return self.__totalstudies

    @property
    def totalvalidsequences(self):
        return self.__totalvalidseq

    @property
    def totalinvalidsequences(self):
        return len(self.__invalidseq)

    @property
    def totalbadfiles(self):
        return len(self.__notprocessed)
