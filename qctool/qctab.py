# qctab.py

"""
Created on 31/7/2018

@author: Iosif Spartalis

Quality Control tool for tabular data


"""
import argparse
import os
import pandas as pd
from qctablib import DatasetCsv, Metadata

if __name__ == '__main__':
    # Create a parser
    PARSER = argparse.ArgumentParser(description="A tool that provides a \
                                     statistical report about the \
                                     input csv file.")
    PARSER.add_argument("--input_csv", type=str,
                        help="dataset input csv")
    PARSER.add_argument("--meta_csv", type=str,
                        help="variables metadata csv")
    PARSER.add_argument("--col_val", type=str,
                        help="the column with variable name \
                        in metadata file")
    PARSER.add_argument("--col_type", type=str,
                        help="the column with variable type \
                        in metadata file")
    ARGS = PARSER.parse_args()
    METADATA = None
    # Get the filename and dataset name
    FILENAME = os.path.basename(ARGS.input_csv)
#    INPUT_PATH = Path(ARGS.input_csv)
#    FILENAME = INPUT_PATH.name

#    DATASET_NAME = INPUT_PATH.stem
    DATASET_NAME = os.path.splitext(FILENAME)[0]
    # Get the path of the csv file
    path = os.path.dirname(os.path.abspath(ARGS.input_csv))

    if ARGS.meta_csv:
        METADATA = Metadata.from_csv(ARGS.meta_csv, ARGS.col_val, ARGS.col_type)
    else:
        METADATA = None
    DATA = pd.read_csv(ARGS.input_csv, index_col=None)
    testcsv = DatasetCsv(DATA, FILENAME, METADATA)
#    exportfile_ds = os.path.join(path, dataset_name
#                                 + '_dataset_report.csv')
    exportfile = os.path.join(path, DATASET_NAME + '_report.csv')
    exportfile_ds = os.path.join(path, DATASET_NAME + '_dataset_report.csv')
    exportfile_pdf = os.path.join(path, DATASET_NAME + '_report.pdf')
    exportfile_tex = os.path.join(path, DATASET_NAME +  '_report')

    testcsv.export_dstat_csv(exportfile_ds, need_readable=True)
    testcsv.export_vstat_csv(exportfile, need_readable=True)
    testcsv.export_latex(exportfile_tex, pdf=True)
