# patient.py


class MRIPatient(object):
    """
    A class for a patient that have performed MRI scans
    """
    def __init__(self, patientid, studies):
        self.__patientid = patientid
        self.__studies = studies
        self.__studies.sort(key=lambda x: x.studydate)

    @property
    def patientid(self):
        return self.__patientid

    @property
    def studies(self):
        return self.__studies
