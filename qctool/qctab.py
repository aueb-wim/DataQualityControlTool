# qctab.py

"""
Created on 31/7/2018

@author: Iosif Spartalis

Quality Control tool for tabular data


"""
# TODO: Build unit tests

import argparse
import os
import logging
import datetime
import pandas as pd

__version__ = '0.0.1'
DIR_PATH = os.path.dirname(os.path.realpath(__file__))

# Create and configure logger
LOG_FORMAT = "%(levelname)s %(asctime)s - %(message)s"
logging.basicConfig(filename=os.path.join(DIR_PATH, 'lumperjack.log'),
                    level=logging.DEBUG,
                    format=LOG_FORMAT,
                    filemode='w')
LOGGER = logging.getLogger()


def outliers(numbers, times):
    """Returns the number of outliers of a given list of numbers.
    Outlier is consider the value which is outside (times * std deviations)
    w/r of the avarage value

    numbers -> array or pandas Series
    times -> how many times bigger from the std deviation will
             be the space which outside values would be considered as outliers.

    Returns an intenger

    """

    # TODO: Add  checks, asserts and exceptions

    mean, std = numbers.mean(), numbers.std()
    # Define upper bound of the space of non-outliers
    upper = mean + times * std
    # Define the lower bound of the space of non-outliers
    lower = mean - times * std
    # Return how many values are not inside this space
    return len(numbers[(numbers < lower) | (numbers > upper)])


class DatasetCsv(object):
    """This class is for producing a statistical report about
    a given csv dataset
    """
    def __init__(self, csvfile, metafile=None):
        """csvfile is the path for the hospitals dataset csvfile and the
        metafile is the path of the csv file with the metadata of the
        hospital dataset csv file
        """
        # TODO: update the docstring
        # TODO: add exceptions
        # TODO: add outlier and total critirion to the arguments
        # TODO: impove the export_html method for prettier results
        # TODO: add export_pdf method

        LOGGER.info("constructor DatasetCsv({0}, {1})".format(csvfile, metafile))
        self.required_metadata = ["variable_name", "type"]
        # Contains the possible types of the dataset - is this useful?
        self.variable_types = ["text", "numeric", "date",
                               "nominal", "unspecified"]

        try:
            # Read the dataset csv file without declared dtypes
            # This has the effect that the dates and categorical
            # variables will be represented as 'object' dtype
            LOGGER.debug("# Read the dataset csv file")
            self.data = pd.read_csv(csvfile, index_col=None)
            # TODO: Case where there is no metadata
            # Read the metadata csv file
            LOGGER.debug("# Read the metdata csv file")
            self.metadata = pd.read_csv(metafile, index_col=None)

            # Get the filename
            self.filename = os.path.basename(csvfile)

            # Get the path of the csv file
            self.path = os.path.dirname(os.path.abspath(csvfile))

            # get the column id name from the first column of the dataset
            self.id_column= self.data.columns[0]
            # check if id_column exist in the dataset csv
#            if id_column not in self.data.columns:
#                raise Exception \
#                    ("'{0}' column not found  in the {1} dataset file".format(id_column,
#                                                                              self.filename))
            # check if the required columns are in the metadata csv
            if not all(column in self.metadata.columns for column in self.required_metadata):
                raise Exception \
                    ("'variable_name' or 'type' is not found in the metadata csv")

        except IOError as e:
            print(e)

        else:

            LOGGER.debug(" Get the filename without the extension")
            self.dataset_name = os.path.splitext(self.filename)[0]

            # Create a pandas dataframe attribute for dataset statistics
            # self.datasetstats
            self._create_dstats_df()

            # Create a pandas dataframe attribute for variable statistics
            # self.variablestats
            self._create_vstats_df()
            self._calc_vstat_outliers(3)

            # Check the metadata content
            # self._check_metadata()

            # Calc dataset statistics
            self.calcdataset(self.id_column)

    def _create_dstats_df(self):
        """ Create a pandas dataframe attribute for dataset statistics,
            datasetstat
        """
        text_columns = ['name_of_file', 'qctool_version']
        date_columns = ['date_qc_ran']
        numeric_columns = ['total_variables', 'total_rows', 'rows_only_id',
                           'rows_no_id', 'rows_complete']
        column_names = text_columns + date_columns + numeric_columns
        self.datasetstats = pd.DataFrame(columns=column_names)
        # convert dataframe column dtypes from string to date and numeric
        for cname in date_columns:
            self.datasetstats[cname] = self.datasetstats[cname].apply(pd.to_datetime)
        for cname in numeric_columns:
            self.datasetstats[cname] = self.datasetstats[cname].apply(pd.to_numeric)

    def _create_vstats_df(self):
        """ Create a pandas dataframe attribute for variable
        statistics, variablestats
        """


        # Create an empty dataframe with the column 'variable_name'
        basic_columns = ['variable_name']
        df1 = pd.DataFrame(columns=basic_columns)

        # Fill the df with the variables names aka columns of the dataset csv
        df1['variable_name'] = self.data.columns

        # Calculate descriptive statistics for all types of the
        # dataset variables and store it to a dataframe.
        df_desc = self.data.describe(include='all').transpose()
        df_desc['variable_name'] = df_desc.index

        # Merge the dataframe with the statistics with the main dataframe
        df1 = df1.merge(df_desc, on='variable_name', how='left')
        df_desc = None

        # TODO: Check if exist the metadata dataframe!!!
        # Merge the metadata dataframe with the main dataframe
        df1 = df1.merge(self.metadata, on='variable_name',
                        suffixes=('_qctool', '_metadata'), how='left')

        # Calculate the not null percentage per variable
        df1['not_null_%'] = df1['count']/len(self.data) * 100
        df1['not_null_%'] = df1['not_null_%'].apply(lambda x: round(x, 2))

        # Calculate the number of outliers per numerical variable
        df_outliers = self._calc_vstat_outliers(3)
        df_outliers['variable_name'] = df_outliers.index
        df1 = df1.merge(df_outliers, on='variable_name', how='left')

        # Place the variables to buckets according to its
        # not null percentage
        # NOTE: the 100% bin is filled with values 99.99-100
        var_labels = ['#_0-19.99%', '#_20-39.99%', '#_40-59.99%',
                      '#_60-79.99%', '#_80-99.99%', '#_100%']
        var_bins = [0, 19.99, 39.99, 59.99, 79.99, 99.99, 100]
        df1['not_null_bins'] = pd.cut(df1['not_null_%'], bins=var_bins,
                                      labels=var_labels, include_lowest=True)

        # Estimate the data types of the variables without using
        # the metadata csv
        df1 = df1.merge(self._rough_estimate_types(), on='variable_name',
                        how='left')

        # TODO: check if metadata file exist else use the 'type_estimated'
        # Get the variable names that are declared categorical
        # in the metadata
        cat_criterion = df1['type'].map(lambda x: x == 'nominal')
        meta_categories = list(df1.loc[cat_criterion, 'variable_name'])
        df1 = df1.merge(self._calc_categories(meta_categories),
                        on='variable_name', how='left')

        # Get the top and bottom values of the text variables
        # (dates are considered as text too)
        text_criterion1 = df1['type_estimated'].map(lambda x: x == 'text')
        text_criterion2 = df1['type'].map(lambda x: x != 'nominal')
        text_variables = list(df1.loc[text_criterion1 & text_criterion2,
                                      'variable_name'])
        df1 = df1.merge(self._calc_string_values(text_variables, 5),
                        on='variable_name', how='left')

        # TODO: reorder the columns
        ordered_columns = ['variable_name', 'type', 'type_estimated',
                           'category_levels', 'total_levels',
                           'unique', 'top', 'freq',
                           'count', 'not_null_%',
                           'mean', 'std', 'min', 'max',
                           '25%', '50%', '75%', '#_of_outliers',
                           'bottom_5_text_values', 'top_5_text_values',
                           'comments']

        LOGGER.debug(df1.dtypes)
        self.variablestats = df1

    def _calc_categories(self, cat_variables):
        """ Returns the categories and the number of categories of the given
        nominal varables.
        """
        category_values = []
        total_categories = []
        for variable in cat_variables:
            # get all the values of the current variable and store them
            values_list = list(self.data[variable].value_counts().index)
            category_values.append(str(values_list).strip('[]'))
            # count and store them
            total_categories.append(len(values_list))
        return pd.DataFrame({'variable_name': cat_variables,
                             'category_levels': category_values,
                             'total_levels': total_categories})

    def _calc_string_values(self, text_variables, total):
        """Returns the total top and total bottom variable values
        in respect to their frequency.
        """
        top_values = []
        bottom_values = []
        for variable in text_variables:
            # get all the values of the current variable and store them
            values = self.data[variable].value_counts()
            top = list(values.head(total).index)
            bottom = list(values.tail(total).index)
            top_values.append(str(top).strip('[]'))
            bottom_values.append(str(bottom).strip('[]'))
        return pd.DataFrame({'variable_name': text_variables,
                             'top_{0}_text_values'.format(total): top_values,
                             'bottom_{0}_text_values'.format(total): bottom_values})

    def _calc_vstat_outliers(self, times):
        """Calculates the # of outliers per numerical variable
        returns a df with a column '#_of_outliers' and as index is used
        the numerical variables names
        """
        numeric_variables = self.data.select_dtypes(include=['float64','int64']).columns
        df1 = pd.DataFrame(index = numeric_variables, columns=["#_of_outliers"])
        for variable in numeric_variables:
            df1.at[variable, "#_of_outliers"] = outliers(self.data[variable], times)
        return df1

    def _rough_estimate_types(self):
        """Estimates the data type of the dataset variables"""

        # Find the numerical variables in the dataset and store them in a dataframe
        numeric_variables = self.data.select_dtypes(include=['float64','int64']).columns
        df_numeric = pd.DataFrame(index=numeric_variables,
                                  columns=['type_estimated'])
        df_numeric['type_estimated'] = 'numeric'

        # The rest variables in the dataset are object type
        other_variables = self.data.select_dtypes(exclude=['float64', 'int64']).columns
        df_other = pd.DataFrame(index=other_variables, columns=['type_estimated'])
        df_other['type_estimated'] = 'text'

        # return the concatenation of those dataframes
        df_result = pd.concat([df_numeric, df_other])
        df_result['variable_name'] = df_result.index
        return df_result

    def _make_readable_datasetstats(self):
        """Returns a datasetstats df with more readable columns names."""
        new_columns = {"rows_only_id": "rows with only id",
                       "rows_no_id": "rows with no id",
                       "rows_complete": "rows with all columns filled",
                       "#_0-19.99%": "number of variables with 0-19.99% records filled in",
                       "#_20-39.99%": "number of variables with 20-39.99% records filled in",
                       "#_40-59.99%": "number of variables with 40-59.99% records filled in",
                       "#_60-79.99%": "number of variables with 60-79.99% records filled in",
                       "#_80-99.99%": "number of variables with 80-99.99% records filled in",
                       "#_100%": "number of variables with 100% records filled in"}
        return self.datasetstats.rename(columns=new_columns)



    def calcdataset(self, id_column):
        """Method that calculates the dataset stats and update the datasetstats property.
        """
        # TODO: correct the __version__

        # name_of_file, date_qc_ran, qctool_version, total_rows, total_variables
        self.datasetstats.at[0, 'name_of_file'] = self.dataset_name
        # Get the current date
        LOGGER.debug('# Get the current date')
        self.datasetstats.at[0, 'date_qc_ran'] = pd.to_datetime(datetime.datetime.now())
        self.datasetstats.at[0, 'qctool_version'] = __version__
        self.datasetstats.at[0, 'total_rows'] = self.data.shape[0]
        self.datasetstats.at[0, 'total_variables'] = self.data.shape[1]

        # rows_no_id
        criterion = self.data[id_column].map(lambda x: pd.isnull(x))
        # Find the number of rows with no patient id
        LOGGER.debug(" # Find the number of rows with no patient id")
        self.datasetstats.at[0, "rows_no_id"] = self.data[criterion].shape[0]

        # rows_only_id
        # Find the number of rows with only patient id and no data at all
        LOGGER.debug(" # Find the number of rows with only patient id")
        dataset_columns = list(self.data.columns) # get the columns names of the dataset
        dataset_columns.remove(id_column)  # remove the patient id column
        df_temp1 = self.data[dataset_columns].isnull()
        self.datasetstats.at[0, 'rows_only_id'] = sum(df_temp1.all(axis=1))
        df_temp1 = None

        # rows_complete
        # Find the number of rows with all the columns being filled
        df_temp1 = ~self.data.isnull() # reverse the boolean values
        self.datasetstats.at[0, 'rows_complete'] = sum(df_temp1.all(axis=1))
        df_temp1 = None

        # '#_0-19.99%', '#_20-39.99%', '#_40-59.99%','#_60-79.99%'
        # '#_80-99.99%', '#_100%'
        # get the counts of variables not null categories
        notnullcat = self.variablestats.loc[:, 'not_null_bins'].value_counts(dropna=False)
        # convert the Series item to df, transpose so categories become columns
        # and drop index
        notnullcat = notnullcat.to_frame().transpose().reset_index(drop=True)
        d = {'#_0-19.99%': [0], '#_20-39.99%': [0], '#_40-59.99%': [0],
             '#_60-79.99%': [0], '#_80-99.99%': [0], '#_100%': [0]}
        df2 = pd.DataFrame(d)
        df2.update(notnullcat)
        self.datasetstats = self.datasetstats.merge(df2,
                                                    left_index=True,
                                                    right_index=True,
                                                    how='left')
        self.datasetstats = self.datasetstats.combine_first(df2)

        # Convert those columns to int64
        columns_integer = ['total_variables', 'total_rows', 'rows_only_id', 'rows_no_id',
                           'rows_complete']
        for column in columns_integer:
            self.datasetstats[column] = self.datasetstats[column].astype('int64')

        # Rearrange the column order of the dataset
        ordered_columns = ['name_of_file', "qctool_version", "total_variables",
                           "total_rows", "rows_only_id", "rows_no_id",
                           "rows_complete", "#_100%", "#_80-99.99%",
                           "#_60-79.99%", "#_40-59.99%", "#_20-39.99%",
                           "#_0-19.99%"]
        self.datasetstats = self.datasetstats[ordered_columns]
        LOGGER.debug(self.datasetstats.columns)

        LOGGER.debug(self.datasetstats.dtypes)

    def export_csv(self, readable_columns=False):
        """Exports the datasetstats and variablestats dataframes to a csv.
        """
        exportfile = os.path.join(self.path, self.dataset_name + '_report.csv')
        exportfile_ds = os.path.join(self.path, self.dataset_name + '_dataset_report.csv')

        # Export to csv with readable column names?
        if readable_columns:
            readable_df_datasetstats = self._make_readable_datasetstats()
            readable_df_datasetstats.to_csv(exportfile_ds, index=False)
        else:
            self.datasetstats.to_csv(exportfile_ds, index=False)

#        self.variablestats.drop(labels=['not_null_bins'],
#                                axis=1).to_csv(exportfile,
#                                                index=False)
        # TODO: remove 'not_null_bins' from the export csv
        self.variablestats.to_csv(exportfile,index=False)

    def export_html(self):
        """Exports the datasetstats and variablestats dataframe to html.
        """
        exporthtml = os.path.join(self.path,
                                  self.filename + '_report_var.html')
        with open(exporthtml, 'w') as fd:
            fd.write(self.variablestats.to_html())


if __name__ == '__main__':
    # Create a parser
    PARSER = argparse.ArgumentParser(description="A tool that provides a \
                                     statistical report about the \
                                     input csv file.")
    PARSER.add_argument("--input_csv", type=str, help="input csv")
    PARSER.add_argument("--meta_csv", type=str, help="metadata csv")
    ARGS = PARSER.parse_args()
    testcsv = DatasetCsv(ARGS.input_csv, ARGS.meta_csv)
    testcsv.export_csv(readable_columns=True)
