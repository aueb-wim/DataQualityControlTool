# mristudy.py

from datetime import datetime


class MRIStudy(object):
    """Class for grouping sequence objects
    that belong to the same scanning session
    aka share the same StudyID
    """

    def __init__(self, patientid, studyid, sequences):
        """
        Arguments:
        :param patientid: string with the patient ID
        :param studyid: string with the study ID for scan session
        :param sequences: list with scanning sequences objects
        """
        self.__patientid = patientid
        self.__studyid = studyid
        self.__sequences = sequences
        self.__studydate = None
        self.__findstudydate()

    def __findstudydate(self):
        values = list(seq.seriesdate for seq in self.__sequences)
        # Get the most frequent date from the sequences as study date
        datestring = max(set(values), key=values.count)
        self.__studydate = datetime.strptime(datestring, '%Y%m%d')


    @property
    def studydate(self):
        return self.__studydate

    @property
    def sequences(self):
        return self.__sequences


