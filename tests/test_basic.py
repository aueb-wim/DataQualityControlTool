# test_basic.py
import os
import pandas as pd
from pandas.util.testing import assert_frame_equal
from qctool.qctab import DatasetCsv


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
    datafile = os.path.join('test_datasets','test_random.csv')
    metafile = os.path.join('test_datasets','test_random_metadata.csv')
    reportfile = os.path.join('test_datasets', 'test_random_report.csv')
    dataset_reportfile =  os.path.join('test_datasets', 'test_random_dataset_report.csv')

    # create a DatasetCsv class instance for the test
    ds = DatasetCsv(datafile,metafile, 'Patient_id')

    # Load the precalculate report for the dataset variables as a dataframe
    report_df = pd.read_csv(reportfile)
    columns_object = ['#_of_outliers']
    columns_float = ['not_null_%', 'count']
    report_df = correct_dtypes(report_df, cfloat=columns_float, cobject=columns_object)

    # Load the precalculate report for the dataset itself as a dataframe
    report_dataset_df = pd.read_csv(dataset_reportfile)
    for column in report_dataset_df.columns:
        report_dataset_df[column] = report_dataset_df[column].astype('object')


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
        select_columns = ['name_of_file', 'total_variables', 'total_rows', 'rows_no_data',
                          'rows_no_id']# '#_80-99.99%', '#_60-79.99%',
                          # '#_100%', '_0-19.99%']
        dirived = self.ds.datasetstats.loc[:, select_columns]
        correct = self.report_dataset_df.loc[:, select_columns]
        assert_frame_equal(dirived, correct)



