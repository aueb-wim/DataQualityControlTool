# __main__.py
""" Command Line Interface for MIP Quality Control Tool
"""
import sys
import argparse
import os
import time
import getpass
import pandas as pd
from .qctablib import DatasetCsv, Metadata
from .dicomreport import DicomReport

DIR_PATH = os.path.dirname(os.path.abspath(__file__))

def main():
    """Main app for quality control tool with CLI"""
    # Create a parser
    parser = argparse.ArgumentParser(description='A tool that provides a \
                                     statistical report about the \
                                     input csv file.')
    parser.add_argument('mode', choices=['csv', 'dicom'],
                        help='csv or dicom report, give keywords from the \
                        list[csv, dicom]')
    parser.add_argument('--loris_folder', type=str,
                        help='the folder path for reorganizing dcm files \
                        for Loris pipeline')
    parser.add_argument('--root_folder', type=str,
                        help='the root folder with dicom files')
    parser.add_argument('--report_folder', type=str,
                        help='the output excel file for \
                        the DICOMs report')
    parser.add_argument('--input_csv', type=str,
                        help='dataset input csv')
    parser.add_argument('--meta_csv', type=str,
                        help='variables metadata csv')
    parser.add_argument('--col_val', type=str,
                        help='the column with variable name \
                        in metadata file')
    parser.add_argument('--col_type', type=str,
                        help='the column with variable type \
                        in metadata file')
    parser.add_argument('--pdf', action='store_true',
                        help='export report in pdf? else \
                        export in Latex')
    parser.add_argument('-r', '--readable', action='store_true',
                        help='export csv with readable column \
                        names?')
    args = parser.parse_args(sys.argv[1:])
    metadata = None
    # if CSV dataset
    if args.mode == 'csv':
        # Get the filename and dataset name
        if os.path.exists(args.input_csv):
            filename = os.path.basename(args.input_csv)
            dataset_name = os.path.splitext(filename)[0]
            # Get the path of the csv file
            path = os.path.dirname(os.path.abspath(args.input_csv))
            # Load the data from csv but treat all columns as strings
            data = pd.read_csv(args.input_csv,
                               index_col=None)
        else:
            raise OSError('Filepath not found')

        if args.meta_csv is not None:
            if os.path.exists(args.meta_csv):
                metadata = Metadata.from_csv(args.meta_csv,
                                             args.col_val,
                                             args.col_type)
            else:
                raise OSError('No metadata file found')
        else:
            # continue with no metadata file
            metadata = None
            print('Continuing with no metadata.'
                  'Varible types will be estimated.')
        # Create the dataset report
        testcsv = DatasetCsv(data, filename, metadata)
        # Export Report files paths and names, csv, pdf or tex
        exportfile = os.path.join(path, dataset_name +
                                  '_report.csv')
        exportfile_ds = os.path.join(path, dataset_name +
                                     '_dataset_report.csv')
        #exportfile_tex = os.path.join(path, dataset_name +
        #                              '_report')
        exportfile_pdf = os.path.join(path, dataset_name +
                                      '_report.pdf')

        testcsv.export_dstat_csv(exportfile_ds, need_readable=args.readable)
        testcsv.export_vstat_csv(exportfile, need_readable=args.readable)
        # testcsv.export_latex(exportfile_tex, pdf=args.pdf)
        if args.pdf:
            testcsv.export_pdf(exportfile_pdf)
    # if DICOM dataset
    elif args.mode == 'dicom':
        # Check if the DICOM root folder exists
        if os.path.exists(args.root_folder):
            dicomreport = DicomReport(args.root_folder, getpass.getuser())
            if not os.path.exists(args.report_folder):
                os.mkdir(args.report_folder)
            dicomreport.writereport(args.report_folder)
            if args.loris_folder:
                if not os.path.exists(args.loris_folder):
                    try:
                        os.mkdir(args.loris_folder)
                    except OSError:
                        raise OSError('Could not create LORIS output folder')
                dicomreport.reorganizefiles(args.loris_folder)
        else:
            raise OSError('Root Folder not found')


if __name__ == '__main__':
    start_time = time.time()
    main()
    print('___ %s seconds ---' % (time.time() - start_time))
