# qcutils.py

import re
import logging
import sys
import pandas as pd

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


COMMIX1 = 'Warning! Mixed type variable.'
COMDATE1 = 'Warning! Dates with multiple formats.'
COMDATE2 = 'Warning! Dates with multiple seperators.'
COMDATE3 = 'Warning! Dates with only 2 digit year.'
COMNUM_DEC = 'Warning! Numerical values with different decimal character.'
COMNUM_MIXED = 'Warning! Numerical values with sufix and without sufixes.'
COMNUM_SUFIXES = 'Warning! Numerical values with multiple sufixes!'

# Date regex expressions

# %d %m %Y, dd-mm-yyyy, dd/mm/yyyy,dd.mm.yyyy
DATE1 = (r'\b(0?[1-9]|[12][0-9]|3[01])'
         r'(?P<sep>[- /.])(0?[1-9]|1[012])'
         r'(?P=sep)(?P<year>(19|20)?\d\d)\b')
# %m %d %Y, mm-dd-yyyy
DATE2 = (r'\b(0?[1-9]|1[012])'
         r'(?P<sep>[- /.])(0?[1-9]|[12][0-9]|3[01])'
         r'(?P=sep)(?P<year>(19|20)?\d\d)\b')
# %Y %m %d, yyyy-mm-dd
DATE3 = (r'\b(?P<year>(19|20)?\d\d)'
         r'(?P<sep>[- /.])(0?[1-9]|1[012])'
         r'(?P=sep)(0?[1-9]|[12][0-9]|3[01])\b')
# %d %b %Y, dd-mon-yyyy
DATE4 = (r'\b(0?[1-9]|[12][0-9]|3[01])'
         r'(?P<sep>[ -]?)[a-zA-Z]{3}'
         r'(?P=sep)(?P<year>(19|20)?\d\d)\b')
# %d %B %Y, dd-month-yyyy
DATE5 = (r'\b(0?[1-9]|[12][0-9]|3[01])'
         r'(?P<sep>[ -]?)[a-zA-Z]{4,}'
         r'(?P=sep)(?P<year>(19|20)?\d\d)\b')
# %b %d %Y, mon-dd-yyyy
DATE6 = (r'\b[a-zA-Z]{3}'
         r'(?P<sep>[ -]?)(0?[1-9]|[12][0-9]|3[01])'
         r'(?P=sep)(?P<year>(19|20)?\d\d)\b')
# %B %d %Y
DATE7 = (r'\b[a-zA-Z]{4,}'
         r'(?P<sep>[ -]?)(0?[1-9]|[12][0-9]|3[01])'
         r'(?P=sep)(?P<year>(19|20)?\d\d)\b')
# ddmmyyyy
DATE8 = (r'\b(0?[1-9]|[12][0-9]|3[01])'
         r'(?P<sep>)(0?[1-9]|1[012])'
         r'(?P=sep)(?P<year>(19|20)\d\d)\b')
# mmddyyyy
DATE9 = (r'\b(0?[1-9]|1[012])'
         r'(?P<sep>)(0?[1-9]|[12][0-9]|3[01])'
         r'(?P=sep)(?P<year>(19|20)\d\d)\b')
# yyyymmdd
DATE10 = (r'\b(?P<year>(19|20)\d\d)'
          r'(?P<sep>)(0?[1-9]|1[012])'
          r'(?P=sep)(0?[1-9]|[12][0-9]|3[01])\b')


def outliers(numbers, times):
    """Returns the number of outliers of a given list of numbers.
    As outliers are considered the values that outside the
    space (mean - times * std, mean + times * std).
    Arguments:
    :param numbers: array or pandas Series
    :param times: number
    :return: an integer
    """
    mean, std = numbers.mean(), numbers.std()
    # Define upper bound of the space of non-outliers
    upper = mean + times * std
    # Define the lower bound of the space of non-outliers
    lower = mean - times * std
    # Return how many values are not inside this space
    return len(numbers[(numbers < lower) | (numbers > upper)])


def check_date(datestr):
    """TBD"""
    dateorder = ['date1', 'date2', 'date3', 'date4',
                 'date5', 'date6', 'date7', 'date8',
                 'date9', 'date10']
    dateregex = {'date1': DATE1, 'date2': DATE2,
                 'date3': DATE3, 'date4': DATE4,
                 'date5': DATE5, 'date6': DATE6,
                 'date7': DATE7, 'date8': DATE8,
                 'date9': DATE9, 'date10': DATE10}
    result = {'datetype': 'Not Date',
              'sep': None,
              'fullyear': None}
    for datetype in dateorder:
        match = re.match(dateregex[datetype], str(datestr))
        if match:
            result['datetype'] = datetype
            result['sep'] = match.group('sep')
            if len(match.group('year')) == 4:
                result['fullyear'] = True
            else:
                result['fullyear'] = False
            # LOGGER.debug('Found a date: %s of type %s', datestr, result['datetype'])
            break
    return result


def check_num(numstr):
    """TBD"""
    result = {'numtype': 'Not Number',
              'hasdecimal': False,
              'decimalchar': None,
              'hassufix': False,
              'sufix': None,
              'nanvalue': None}
    # match (-+) number and sufix 
    # like % percentage, or unit name following 
    # only by one digit i.e. cm3 m2 
    # or unitname inside paretheses i.e. (cm3)
    numregex = (r'^[+-]?\d+(?P<decpart>(?P<decchar>[,\.])\d*)?'
                r'(?P<sufix>\s?(\%|\(?\D+\d?\)?))?$')
    # these are na values recognized by pandas
    pandas_nans = ['', '#N/A', '#N/A N/A', '#NA', '-1.#IND',
                   '-1.#QNAN', '-NaN', '-nan', '1.#IND', '1.#QNAN',
                   'N/A', 'NA', 'NULL', 'NaN', 'n/a', 'nan', 'null']
    if numstr in pandas_nans:
        result['numtype'] = 'na_type'
        result['nanvalue'] = numstr
    else:
        match = re.match(numregex, numstr)
        if match:
            result['numtype'] = 'number'
            if match.group('decpart'):
                result['hasdecimal'] = True
                result['decimalchar'] = match.group('decchar')
            if match.group('sufix'):
                result['hassufix'] = True
                result['sufix'] = match.group('sufix')
    return result


def _count_types(values):
    """Count the data types of the given list of values.
    Arguments:
    :param values: A list with varius values
    :return: a dict {'numerical': count of numerical types,
                     'date': count of date types found,
                     'text': count of text type found,
                     'datetypes': set of different date formats found,
                     'decimalchars': set of decimal chars found,
                     'hassufix': True if the numerical value has suffix,
                     'sufixes': set of suffixis ,
                     'num_mixed': True if case of numerical have values
                                  no and with suffixes,
                     'dateseps': set of date separators ,
                     'fullyear': True if dates have 4 digit year,
                     'vocabulary': set of unique text values,
                     'nanvalues': set of NA values found}
    """
    count_num = 0
    count_dates = 0
    count_texts = 0
    vocabulary = {}
    dformats = set()
    dateseps = set()
    decseps = set()
    nanvalues = set()
    sufixes = set()
    hassufix = False
    hasnosufix = False
    num_mixed = False
    fullyear = 1
    for value in values:
        value = str(value)
        datecheck = check_date(value)
        # case of not date
        if datecheck['datetype'] == 'Not Date':
            numcheck = check_num(value)
            # case of na value
            if numcheck['numtype'] == 'na_type':
                # add the na value to the set
                nanvalues.add(numcheck['nanvalue'])
            # case number
            elif numcheck['numtype'] == 'number':
                count_num += 1
                if numcheck['hasdecimal']:
                    decseps.add(numcheck['decimalchar'])
                # case the value has suffix i.e. units, %
                if numcheck['hassufix']:
                    hassufix = True
                    sufixes.add(numcheck['sufix'])
                else:
                    hasnosufix = True
            # case 'Not Number' aka text
            else:
                count_texts += 1
                if value in vocabulary:
                    vocabulary[value] += 1
                else:
                    vocabulary[value] = 1
        # case of date
        else:
            count_dates += 1
            dformats.add(datecheck['datetype'])
            dateseps.add(datecheck['sep'])
            fullyear *= datecheck['fullyear']
    # convert fullyear to boolean
    if fullyear == 0:
        fullyear = False
    elif fullyear == 1:
        fullyear = True
    if hasnosufix * hassufix == 1:
        num_mixed = True
    return {'numerical': count_num,
            'date': count_dates,
            'text': count_texts,
            'datetypes': dformats,
            'decimalchars': decseps,
            'hassufix': hassufix,
            'sufixes': sufixes,
            'num_mixed': num_mixed,
            'dateseps': dateseps,
            'fullyear': fullyear,
            'vocabulary': vocabulary,
            'nanvalues': nanvalues}


def _add_date_comments(comment, datetypes, seps, fullyear):
    """Add comments to the initial comment for a date type.
    Arguments:
    :param comment: the initial comment string
    :param datetypes: number of different date types
    :param seps: number of different date seperators
    :param fullyear: boolean if the date type values
                     have a 4 digit year(else 2digit)
    :return: string with additional comments
    """
    result = comment
    if datetypes > 1:
        result = ' '.join([result, COMDATE1])
    if seps > 1:
        result = ' '.join([result, COMDATE2])
    if not fullyear:
        result = ' '.join([result, COMDATE3])
    return result


def _add_num_comments(comment, decchars, mixed, sufixes):
    """Add comments to the initial comment for a numerical type.
    Arguments:
    :param comment: string, the initial comment
    :param dechars: int, number of different decimal
                    character found
    :param mixed: boolean, if there are values with and 
                  without sufix
    :param sufixes: list of sufixes found
    """
    result = comment
    # Numerical values with different decimal character
    if decchars > 1:
        result = ' '.join([result, COMNUM_DEC])
    # Numerical values with sufix and without sufixes
    if mixed:
        result = ' '.join([result, COMNUM_MIXED])
    # Numerical values with multiple sufixes!
    if len(sufixes) > 1:
        result = ' '.join([result, COMNUM_SUFIXES])
    # Give the unique sufix
    elif len(sufixes) == 1:
        sufix = list(sufixes)[0]
        sufcomment = _give_com_sufix(sufix)
        result = ' '.join([result, sufcomment])
    return result


def _give_com_sufix(sufixstr):
    """Returns a string with comments about given sufix.
    """
    return 'The numerical value has the suffix: {0}'.format(sufixstr)


def _give_com_na(nastrings, possible=False):
    """Returns a string with comments about na values.
    Arguments:
    :param nastrigns: list with strings, aka na's
    :param possible: boolean, are we sure that those
                     values are na?
    """
    possible_nans = None
    # short the values if are more than one
    if len(nastrings) > 1:
        nans_sorted = sorted(nastrings)
        possible_nans = ','.join(nans_sorted)
    else:
        possible_nans = nastrings[0]

    if possible:
        message = 'Possible NA values are: [{0}].'.format(possible_nans)
    else:
        message = 'The NA values found are: [{0}]'.format(possible_nans)
    return message


def guess_type(values, nominal_levels=10):
    """Estimate the type of the given values.
    Arguments:
    :param values: list of values of varius types
    :return: a tupple (datatype, comment)
             datatype can be {'date', 'numerical', 'text'}
             comment is a simple string
    """
    stats = _count_types(values)
    type_estimate = 'Not estimated'
    comment = ''
    vocabulary_size = len(stats['vocabulary'])
    # case of date type
    if stats['date'] > 0:
        type_estimate = 'date'
        count_datetypes = len(stats['datetypes'])
        count_dateseps = len(stats['dateseps'])
        comment = _add_date_comments(comment,
                                     count_datetypes,
                                     count_dateseps,
                                     stats['fullyear'])
        # case of mixed typed values
        if stats['numerical'] > 0 or stats['text'] > 0:
            comment = ' '.join([comment, COMMIX1])
    # case of numerical type
    elif stats['date'] == 0 and stats['numerical'] > 0:
        type_estimate = 'numerical'
        # case of mixed typed values
        if stats['text'] > 0:
            comment = ' '.join([comment, COMMIX1])
    # case of text type
    elif stats['date'] == 0 and stats['numerical'] == 0 and stats['text'] > 0:
        if vocabulary_size <= nominal_levels:
            type_estimate = 'nominal'
        else:
            type_estimate = 'text'
    # add comment about the na values found
    # if len(stats['nanvalues']) > 0:
    #     nanlist = list(stats['nanvalues'])
    #     comment = ' '.join([comment, _give_com_na(nanlist)])

    # check if there are at most 3 unique text values
    # possible nan or other special value
    # if (type_estimate == 'date' or type_estimate == 'numerical'):
    #    if vocabulary_size > 0 and vocabulary_size <= 3 :
    #        possible_nans = list(stats['vocabulary'].keys())
    #        comment = ' '.join([comment, _give_com_na(possible_nans,
    #                                                  possible=True)])
    return type_estimate, comment
