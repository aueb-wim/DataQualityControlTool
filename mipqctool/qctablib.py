#!/usr/bin/env python3
# qctablib.py
"""
Created on 31/7/2018

@author: Iosif Spartalis

library for profiling tabular data


"""

# TODO: Build unit tests


import os
import datetime
import logging
import sys
import pandas as pd
from . import qcexport, qcutils, qcpdutils, __version__
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

COLUMNS_NUM = ['variable_name', 'type', 'type_estimated',
               'count', 'not_null_%',
               'mean', 'std', 'min', 'max',
               '25%', '50%', '75%', '#_of_outliers',
               'comments']

COLUMNS_NOM = ['variable_name', 'type', 'type_estimated',
               'category_levels', 'total_levels',
               'unique', 'top', 'freq',
               'count', 'not_null_%',
               'comments']

COLUMNS_TEXT = ['variable_name', 'type', 'type_estimated',
                'unique', 'top', 'freq',
                'count', 'not_null_%',
                'bottom_5_text_values', 'top_5_text_values',
                'comments']

READABLE_VCOLUMMS = {'type': 'type declared',
                    'category_levels': 'list of category values',
                    'total_levels': 'number of category values',
                    'unique': 'count of unique values (for text variables)',
                    'top': 'most frequent value (for text variables)',
                    'freq': ('number of occurrences for most frequent'
                            ' value (for text variables)'),
                    'count': 'count of records filled in',
                    'not_null_%': '% of not null rows',
                    '25%': ('25% of records are below this value'
                            '(limit value of the first quartile)'),
                    '50%': '50% of records are below this value (median)',
                    '75%': ('75% of records are below this value'
                            '(limit value of the third quartile)'),
                    '#_of_outliers': '#_of_outliers(outside 3 std.dev)',
                    'bottom_5_text_values': '5 least frequent values',
                    'top_5_text_values': '5 most frequent values'}

READABLE_DCOLUMNS = {"rows_only_id": "rows with only id",
                    "rows_no_id": "rows with no id",
                    "rows_complete": "rows with all columns filled",
                    "#_0-19.99%": "number of variables with 0-19.99% records filled in",
                    "#_20-39.99%": "number of variables with 20-39.99% records filled in",
                    "#_40-59.99%": "number of variables with 40-59.99% records filled in",
                    "#_60-79.99%": "number of variables with 60-79.99% records filled in",
                    "#_80-99.99%": "number of variables with 80-99.99% records filled in",
                    "#_100%": "number of variables with 100% records filled in"}

class Metadata(object):
    """Class for manupulating metadata files"""
    # TODO: implement class methods for loading json
    def __init__(self, dataframe, col_val, col_type):
        """
        Arguments:
        :param dataframe: a pandas dataframe with metadata
        :param col_val: metadata column with the variable codes
        :param col_type: metadata column with the variable types
        """
        if isinstance(dataframe, pd.core.frame.DataFrame):
            self.defined_columns = ['variable_name', 'type']
        else:
            raise Exception("Give as input a pandas dataframe!")

        if not all(column in dataframe.columns for column in [col_val, col_type]):
            raise Exception(
                "{0} or {1} is not found in the metadata".format(col_val,
                                                                 col_type))
        new_columns = dict(zip([col_val, col_type],
                               self.defined_columns))
        self.meta = dataframe.rename(columns=new_columns)
        self.meta.set_index('variable_name', drop=False, inplace=True)

    @classmethod
    def from_csv(cls, filename, col_val, col_type, **kwargs):
        """Constructor using a metadata csv file.
        Arguments:
        :param filename: filepath of the metadata csv
        :param col_val: metadata column with the variable codes
        :param col_type: metadata column with the variable types
        """
        data = pd.read_csv(filename, **kwargs)
        return cls(data, col_val, col_type)


class VariableStats(object):
    """Class for calculating statistics of a hospital tabular dataset.
    """
    _metadata = None
    # The metadata columns that are used in this class
    meta_columns = ['variable_name', 'type']

    # The dataframe with variable statistics will have these columns
    basic_columns = ['variable_name', 'type', 'type_estimated',
                     'category_levels', 'total_levels',
                     'unique', 'top', 'freq',
                     'count', 'not_null_%',
                     'mean', 'std', 'min', 'max',
                     '25%', '50%', '75%', '#_of_outliers',
                     'bottom_5_text_values', 'top_5_text_values',
                     'not_null_bins', 'comments']

    def __init__(self, dataset, metadata=None):
        """
        Arguments:
        :param dataset: pandas DataFrame with hospital data, must all columns
                        be dtype object.
        :param metadata: pandas DataFrame with metadata about the variables
                         has to have a column 'type'
        """
        if isinstance(dataset, pd.core.frame.DataFrame):
            self.data = dataset
            # fill the nan values with empty strings
            # self.data.fillna('', inplace=True)
        else:
            raise Exception("Give as input a Pandas Dataframe!")
        self.metadata = metadata
        self.vstats = self.create_emtpy_vstat_df(self.basic_columns)
        self.categorical = None
        self.numerical = None
        self.text = None
        self.dates = None
        self._fill_vstats()

    @property
    def metadata(self):
        """Returns the metadata dataframe"""
        return self._metadata

    @metadata.setter
    def metadata(self, mdata):
        """Sets the metadata dataframe from a Metadata object"""
        if isinstance(mdata, Metadata):
            if isinstance(self._metadata, pd.core.frame.DataFrame):
                self._metadata.update(mdata.meta[self.meta_columns])
            else:
                self._metadata = mdata.meta[self.meta_columns]
        else:
            self._metadata = None

    def create_emtpy_vstat_df(self, columns):
        """Returns a Dataframe with empty rows and given columns.
        Arguments:
        :param columns: a list of column names
        :return : pandas dataframe with the column variable_name filled with
        the dataset variable codes and all the other columns filled with
        NaNs
        """
        new_df = pd.DataFrame(index=self.data.columns, columns=columns)
        # Fill the df with the variables names aka columns of the dataset csv
        new_df['variable_name'] = new_df.index
        return new_df

    def _fill_vstats(self):
        """Fill the vstats dataframe with statistics about dataset
        variables"""

        df1 = self.create_emtpy_vstat_df(self.basic_columns)
        # Estimate the data types of the variables without using
        # the metadata csv
        df1.update(qcpdutils.rough_estimate_types(self.data))

        # Check if exist the metadata dataframe
        # update the main dataframe
        # Get the variable names that are declared categorical
        # in the metadata
        type_column = 'type_estimated'
        if isinstance(self.metadata, pd.core.frame.DataFrame):
            df1.update(self.metadata)
            type_column = 'type'

        cat_criterion = df1[type_column].map(lambda x: str(x).lower() == 'nominal')
        num_criterion = df1[type_column].map(lambda x: str(x).lower() == 'numerical')
        date_criterion = df1[type_column].map(lambda x: str(x).lower() == 'date')
        text_criterion = df1[type_column].map(lambda x: str(x).lower() == 'text')
        self.categorical = list(df1.loc[cat_criterion, 'variable_name'])
        self.numerical = list(df1.loc[num_criterion, 'variable_name'])
        self.dates = list(df1.loc[date_criterion, 'variable_name'])
        self.text = list(df1.loc[text_criterion, 'variable_name'])
    
        df1.update(qcpdutils.calc_categories(self.data, self.categorical))

        # Calculate descriptive statistics for all types of the
        # dataset variables and store it to a dataframe.
        # TODO: try statment in case no numerical variable presence
        df_desc = self.data.describe(include='all').transpose()
        clmround = ['mean', 'std', 'min', 'max',
                    '25%', '50%', '75%']
        df_desc[clmround] = df_desc[clmround].applymap(lambda x: round(x, 4))
        df1.update(df_desc)
        df_desc = None

        # Calculate the not null percentage per variable
        df1['not_null_%'] = df1['count']/len(self.data) * 100
        df1['not_null_%'] = df1['not_null_%'].apply(round, ndigits=2)

        # Calculate the number of outliers per numerical variable
        df_outliers = qcpdutils.calc_outliers(self.data, 3)
        df1.update(df_outliers)
        df_outliers = None

        # Place the variables to buckets according to its
        # not null percentage
        # NOTE: the 100% bin is filled with values 99.99-100
        var_labels = ['#_0-19.99%', '#_20-39.99%', '#_40-59.99%',
                      '#_60-79.99%', '#_80-99.99%', '#_100%']
        var_bins = [0, 19.99, 39.99, 59.99, 79.99, 99.99, 100]
        df1['not_null_bins'] = pd.cut(df1['not_null_%'], bins=var_bins,
                                      labels=var_labels, include_lowest=True)

        # Get the top and bottom values of the text variables
        # (dates are considered as text too)
        text_criterion1 = df1['type_estimated'].map(lambda x: x == 'text')
        text_criterion2 = df1['type'].map(lambda x: str(x).lower() != 'nominal')
        text_variables = list(df1.loc[text_criterion1 & text_criterion2,
                                      'variable_name'])
        df1.update(qcpdutils.calc_topstrings(self.data, text_variables, 5))
        self.vstats.update(df1)

    def get_readable_vstats(self):
        """Returns a variablestats df with more readable columns names."""
        new_columns = {'type': 'type declared',
                       'category_levels': 'list of category values',
                       'total_levels': 'number of category values',
                       'unique': 'count of unique values (for text variables)',
                       'top': 'most frequent value (for text variables)',
                       'freq': ('number of occurrences for most frequent'
                                ' value (for text variables)'),
                       'count': 'count of records filled in',
                       'not_null_%': '% of not null rows',
                       '25%': ('25% of records are below this value'
                               '(limit value of the first quartile)'),
                       '50%': '50% of records are below this value (median)',
                       '75%': ('75% of records are below this value'
                               '(limit value of the third quartile)'),
                       '#_of_outliers': '#_of_outliers(outside 3 std.dev)',
                       'bottom_5_text_values': '5 least frequent values',
                       'top_5_text_values': '5 most frequent values'}
        return self.vstats.rename(columns=new_columns)


class DatasetCsv(VariableStats):
    """This class is for producing a statistical report about
    a given csv dataset
    """

    def __init__(self, data, dname, metadata=None):
        """ data -> pandas dataframe
        dname -> a string with the name of dataset file
        hospital dataset csv file
        """
        # TODO: update the docstring
        # TODO: add exceptions
        # TODO: add outlier and total critirion to the arguments
        # Read the dataset csv file without declared dtypes
        # This has the effect that the dates and categorical
        # variables will be represented as 'object' dtype
        super().__init__(data, metadata)
        LOGGER.info('Started processing the csv')
        self.id_column = self.data.columns[0]
        self.dataset_name = dname

        # self.datasetstats
        self.dstats = {}
        self._initialize_dstats()
        # Calc dataset not null % categories
        self._calc_dstats_notnnullcat()

    def _initialize_dstats(self):
        """Initialize the dict dstats with the some statistics about the
            dataset
        """
        id_column = self.id_column
        self.dstats['name_of_file'] = self.dataset_name
        dt_run = datetime.datetime.now()
        self.dstats['date_qc_ran'] = dt_run.strftime('%Y-%m-%d %H:%M:%S')
        self.dstats['qctool_version'] = __version__
        self.dstats['total_rows'] = self.data.shape[0]
        self.dstats['total_variables'] = self.data.shape[1]

        # rows_no_id
        criterion = self.data[id_column].map(lambda x: pd.isnull(x))
        # Find the number of rows with no patient id
        self.dstats['rows_no_id'] = self.data[criterion].shape[0]

        # rows_only_id
        # Find the number of rows with only patient id and no data at all
        # get the columns names of the dataset
        dataset_columns = list(self.data.columns)
        dataset_columns.remove(id_column)  # remove the patient id column
        df_temp1 = self.data[dataset_columns].isnull()
        self.dstats['rows_only_id'] = sum(df_temp1.all(axis=1))
        df_temp1 = None

        # rows_complete
        # Find the number of rows with all the columns being filled
        df_temp1 = ~self.data.isnull()  # reverse the boolean values
        self.dstats['rows_complete'] = sum(df_temp1.all(axis=1))
        df_temp1 = None

        # '#_0-19.99%', '#_20-39.99%', '#_40-59.99%','#_60-79.99%'
        # '#_80-99.99%', '#_100%'
        d = {'#_0-19.99%': 0, '#_20-39.99%': 0, '#_40-59.99%': 0,
             '#_60-79.99%': 0, '#_80-99.99%': 0, '#_100%': 0}
        self.dstats.update(d)

    def _calc_dstats_notnnullcat(self):
        """Updates the dstats with the # of variables
        are in the 6 not null % categories
        """
        # '#_0-19.99%', '#_20-39.99%', '#_40-59.99%','#_60-79.99%'
        # '#_80-99.99%', '#_100%'
        # get the counts of variables not null categories
        notnullcat = self.vstats.loc[:, 'not_null_bins'].value_counts(dropna=False)
        # convert the Series item to df, transpose so categories become columns
        # and drop index
        notnullcat = notnullcat.to_frame().transpose().reset_index(drop=True)
        dict_notnull = qcpdutils.pandas2dict(notnullcat)
        self.dstats.update(dict_notnull)

    def _dstat_2_df(self, readable=False):
        """Converts the dstat dictionary to pandas df"""
        dstats_df = pd.DataFrame(qcpdutils.dict4pandas(self.dstats))
        # Rearrange the column order of the dataset
        ordered_columns = ['name_of_file', 'date_qc_ran', "qctool_version",
                           "total_variables",
                           "total_rows", "rows_only_id", "rows_no_id",
                           "rows_complete", "#_100%", "#_80-99.99%",
                           "#_60-79.99%", "#_40-59.99%", "#_20-39.99%",
                           "#_0-19.99%"]
        dstats_df = dstats_df[ordered_columns]
        if readable:
            new_columns =\
                {"rows_only_id": "rows with only id",
                 "rows_no_id": "rows with no id",
                 "rows_complete": "rows with all columns filled",
                 "#_0-19.99%": "number of variables with 0-19.99% records filled in",
                 "#_20-39.99%": "number of variables with 20-39.99% records filled in",
                 "#_40-59.99%": "number of variables with 40-59.99% records filled in",
                 "#_60-79.99%": "number of variables with 60-79.99% records filled in",
                 "#_80-99.99%": "number of variables with 80-99.99% records filled in",
                 "#_100%": "number of variables with 100% records filled in"}
            dstats_df.rename(columns=new_columns, inplace=True)
        return dstats_df

    def export_dstat_csv(self, filepath, need_readable=False):
        """Exports the datasetstats and variablestats dataframes to a csv.
        """
        datasetstats = self._dstat_2_df(need_readable)
        datasetstats.to_csv(filepath, index=False)

    def export_vstat_csv(self, filepath, need_readable=False):
        """Exports the variable statistics to a csv"""
        # Export to csv with readable column names?
        if need_readable:
            readable_df_vstats = self.get_readable_vstats()
            readable_df_vstats.drop(labels=['not_null_bins'],
                                    axis=1).to_csv(filepath,
                                                   index=False)
        else:
            self.vstats.drop(labels=['not_null_bins'],
                             axis=1).to_csv(filepath,
                                            index=False)

    def export_latex(self, filepath, pdf=False):
        """Produces a dataset statistical report in LaTex format.
        """
        # dstat process
        dstat = self._dstat_2_df(readable=True).transpose()
        # Override the predicted type and use pandas estimation
        # TODO: make the tool robust for calculating stats of mixed type variables
        numerical = list(self.data.select_dtypes(include=['float64', 'int64']).columns)
        not_text = numerical.copy()
        not_text.extend(self.categorical)
        LOGGER.debug('numerical columns are: {}'.format(' '.join(numerical)))
        LOGGER.debug('not text columns are: {}'.format(' '.join(not_text)))
        # find the rest of the columns
        all_others = [column for column in self.data.columns if column not in not_text]
        num = nom = self.vstats.loc[numerical, COLUMNS_NUM].rename(columns=READABLE_VCOLUMMS)
        nom = self.vstats.loc[self.categorical, COLUMNS_NOM].rename(columns=READABLE_VCOLUMMS)
        other = self.vstats.loc[all_others, COLUMNS_TEXT].rename(columns=READABLE_VCOLUMMS)

        vstat = [num, nom, other]

        qcexport.latex2pdf(filepath, dstat, vstat, exportpdf=pdf)
