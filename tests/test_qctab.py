# test_qctab.py

import os
import logging
import pandas as pd
from pandas.util.testing import assert_frame_equal
from qctool.qctab import DatasetCsv

DIR_PATH=os.path.dirname(os.path.realpath(__file__))


LOG_FORMAT = "%(levelname)s %(asctimes)s - %(message)s"
logging.basicConfig(filename=os.path.join(DIR_PATH, 'test_qctab.log'),
                                          level=logging.DEBUG,
                                          format=LOG_FORMAT,
                                          filemode='w')
test_logger = logging.getLogger()

####### dataset report columns ######
dstats_columns_int = ['#_100%','#_80-99.99%', '#_60-79.99%',
                      '#_20-39.99%', '#_0-19.99%']
dstats_columns_float = []
dstats_columns_string = []




def correct_dtypes(dataframe, cfloat=None, cobject=None, cintegers=None):
    """Corrects the column dtypes of the given dtypes
    returns a pandas dataframe
    """
    if cfloat:
        for column in cfloat:
            dataframe[column] = dataframe[column].astype('float64')

    if cobject:
        for column in cobject:
            dataframe[column] = dataframe[column].astype('object')

    if cintegers:
        for column in cintegers:
            dataframe[column] = dataframe[column].astype('int64')

    return dataframe



class Test_dataset_random(object):
    """Test for a test datatest with variables random floats
    dataset file -> test_random.csv
    metadata file -> test_random_metadata.csv
    dataset report -> test_random_dataset_report.csv
    variable report -> test_random_report.csv

    All the above files are produces from the test_random.xlsx file
    """
    datafile = os.path.join('test_datasets','test_random.csv')
    metafile = os.path.join('test_datasets','test_random_metadata.csv')
    reportfile = os.path.join('test_datasets', 'test_random_report.csv')
    dataset_reportfile =  os.path.join('test_datasets', 'test_random_dataset_report.csv')

    # create a DatasetCsv class instance for the test
    ds = DatasetCsv(datafile,metafile)

    # Load the precalculate report for the dataset variables as a dataframe
    report_df = pd.read_csv(reportfile)
    columns_object = ['#_of_outliers']
    columns_float = ['not_null_%', 'count']
    report_df = correct_dtypes(report_df, cfloat=columns_float, cobject=columns_object)

    # Load the precalculate report for the dataset itself as a dataframe
    report_dataset_df = pd.read_csv(dataset_reportfile)
#    integers_columns = ['#_80-99.99%', '#_60-79.99%',
#                          '#_100%', '#_0-19.99%', '#_20-39.99%']

#    for column in integers_columns:
#        report_dataset_df[column] = report_dataset_df[column].astype('int64')


    def test_var_report(self):
        select_columns = ['variable_name', 'count', 'mean', '#_of_outliers',
                          'std','min', '25%' ,'50%', '75%', 'max', 'not_null_%']
        dirived = self.ds.variablestats.loc[:, select_columns]
        # Select only the rows about the variables 1-8
        dirived = dirived.loc[dirived['variable_name'] != 'Patient_id',
                              select_columns]
        dirived = dirived.reset_index(drop=True)
        correct = self.report_df.loc[:, select_columns]
        assert_frame_equal(dirived, correct)

    def test_dataset_report(self):
        select_columns = ['name_of_file', 'total_variables', 'total_rows', 'rows_only_id',
                          'rows_no_id', 'rows_complete','#_80-99.99%', '#_60-79.99%',
                          '#_100%', '#_0-19.99%']
        dirived = self.ds.datasetstats.loc[:, select_columns]
        correct = self.report_dataset_df.loc[:, select_columns]
        test_logger.debug(dirived.dtypes)
        test_logger.debug(correct.dtypes)
        assert_frame_equal(dirived, correct)
