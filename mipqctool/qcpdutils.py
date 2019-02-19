# qcpdutils.py
import pandas as pd
from . import qcutils


def dict4pandas(d):
    """Takes a dict {key : value} and returns dict {key : [value]}"""
    new_dict = {}
    for key in d.keys():
        new_dict[key] = [d[key]]
    return new_dict


def pandas2dict(df):
    """Takes a pd Dataframe and returns
    a dict {column : value} of the first row only"""
    new_dict = df.to_dict(orient='records')
    return new_dict[0]


def guess_nominal(dataframe, threshold):
    """Finds which columns of the dataframe are nominal.
    Arguments:
    :param dataframe: Pandas dataframe
    :param threshold: int the maximum unique string values
                      in order to categorise a column as nominal
    :return: A list with nominal column names
    """
    df_desc = dataframe.describe(include='all').transpose()
    return list(df_desc.loc[df_desc['unique'] <= threshold].index)


def calc_categories(data, cat_variables):
        """Find the categories and the number of categories of the given
        nominal varables.

        Arguments:
        :param data: a pandas DataFrame
        :param cat_variables: list with variable codes which are nominal
        :return: pandas dataframe with 3 columns 'variable_name',
        'category_levels', 'total_levels'. The variables codes are
        used as index.
        """
        category_values = []
        total_categories = []
        for variable in cat_variables:
            # get all the values of the current variable and store them
            values_list = list(data[variable].value_counts().index)
            category_values.append(str(values_list).strip('[]'))
            # count and store them
            total_categories.append(len(values_list))
        result = pd.DataFrame({'variable_name': cat_variables,
                               'category_levels': category_values,
                               'total_levels': total_categories})
        result.set_index('variable_name', drop=False, inplace=True)
        return result


def calc_topstrings(data, text_variables, total):
        """Find variable values with the lowest and the
        higest frequency.

        Arguments:
        :param data: a pandas DataFrame
        :param text_variables: list of variables codes which
        have text values
        :param total: number of variables values with the lowest
        and higher frequency
        """
        top_values = []
        bottom_values = []
        for variable in text_variables:
            # get all the values of the current variable and store them
            values = data[variable].value_counts()
            top = list(values.head(total).index)
            bottom = list(values.tail(total).index)
            top_values.append(str(top).strip('[]'))
            bottom_values.append(str(bottom).strip('[]'))
        result = pd.DataFrame({'variable_name': text_variables,
                               'top_{0}_text_values'.format(total): top_values,
                               'bottom_{0}_text_values'.format(total): bottom_values})
        result.set_index('variable_name', drop=False, inplace=True)
        return result


def calc_outliers(data, times):
        """Calculates the number of outliers per numerical variable.
        As outliers are considered the values that outside the
        space (mean - times * std, mean + times * std)

        Arguments:
        :param data: a pandas DataFrame
        :param times: number
        :returns: pandas df with  column '#_of_outliers' and as index
        is used the variables codes which are numerical """
        numeric_variables = data.select_dtypes(include=['float64', 'int64']).columns
        df1 = pd.DataFrame(index=numeric_variables, columns=["#_of_outliers"])
        for variable in numeric_variables:
            df1.at[variable, "#_of_outliers"] = qcutils.outliers(data[variable],
                                                                 times)
        return df1


def rough_estimate_types(data):
        """Estimates the data type of the dataset variables"""
        all_variables = data.columns
        result = pd.DataFrame(index=all_variables,
                              columns=['type_estimated', 'comments'])
        for variable in all_variables:
            variabledata = data[variable].tolist()
            type_estimated, comment = qcutils.guess_type(variabledata)
            result.at[variable, 'type_estimated'] = type_estimated
            result.at[variable, 'comments'] = comment
        return result
