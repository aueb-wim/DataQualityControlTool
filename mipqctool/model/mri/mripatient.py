# mripatient.py


class MRIPatient(object):
    """
    A class for a patient that have performed MRI scans
    """
    def __init__(self, patientid, studies):

        self.__totalsequences = 0
        self.__seriesdescriptions = set()

        self.__patientid = patientid
        self.__studies = studies
        self.__studies.sort(key=lambda x: x.studydate)

        self.__collect_seq_info()

    @property
    def patientid(self):
        return self.__patientid

    @property
    def studies(self):
        return self.__studies

    @property
    def totalstudies(self):
        return len(self.__studies)
    
    @property
    def totalsequences(self):
        return self.__totalsequences
    
    @property
    def seriesdescriptions(self):
        """A set of seriesdescriptions of the patient sequences"""
        return self.__seriesdescriptions

    # private

    def __collect_seq_info(self):
        totalseq = 0
        for study in self.__studies:
            num_of_seqs = len(study.sequences)
            totalseq += num_of_seqs
            for seq in study.sequences:
                self.__seriesdescriptions.add(seq.seriesdescription)

        self.__totalsequences = totalseq
