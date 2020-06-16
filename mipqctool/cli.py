# cli.py
""" Command Line Interface for MIP Quality Control Tool
"""
import os
import click
import getpass
import json

from .dicomreport import DicomReport
from .tablereport import TableReport
from .qctable import QcTable
from .qcschema import QcSchema

DIR_PATH = os.path.dirname(os.path.abspath(__file__))


@click.group()
def main():
    pass


@main.command()
@click.argument('input_csv', type=click.Path(exists=True))
@click.option('--col_id', type=int, required=True, default=1, show_default=True,
              help='Column number that holds id values (primary key)')
@click.option('--clean', is_flag=True,
              help='Filepath for the new dataset csv file after data cleaning')
@click.option('-m', '--metadata', type=click.Path(exists=True),
              help='Path of the metadata json file with the schema \
                    of the dataset csv file')
@click.option('--max_levels', type=int, default=10, show_default=True,
              help='Max unique values of a text variable \
                    that below that will be infered as nominal \
                    when no dataset metadata (schema) is provided')
@click.option('--sample_rows', type=int, default=100, show_default=True,
              help='Number rows that are going to be used as sample \
                    for infering the dataset metadata (schema) when \
                    metadata file is not provided')
def csv(input_csv, col_id, clean,
        metadata, sample_rows, max_levels):
    filename = os.path.basename(input_csv)
    dataset_name = os.path.splitext(filename)[0]
    report_name = dataset_name + '_report.pdf'
    # Get the path of the csv file
    path = os.path.dirname(os.path.abspath(input_csv))

    # check if metadata json is provided
    if metadata:
        with open(metadata) as json_file:
            dict_schema = json.load(json_file)
        schema = QcSchema(dict_schema)
        dataset = QcTable(input_csv, schema=schema)
    else:
        dataset = QcTable(input_csv, schema=None)
        dataset.infer(limit=sample_rows, maxlevels=max_levels)
    datasetreport = TableReport(dataset, col_id)

    # Apply data cleaning corrections?
    if clean:
        datasetreport.apply_corrections()
        datasetreport.save_corrected(input_csv)

    datasetreport.printpdf(os.path.join(path, report_name))


@main.command()
@click.argument('root_folder', type=click.Path(exists=True))
@click.argument('report_folder', type=click.Path())
@click.option('--loris_folder', type=click.Path(),
              help='')
def dicom(ctx, root_folder, report_folder, loris_folder=None):
    if loris_folder and len(os.listdir(loris_folder)) != 0:
        raise Exception('LORIS output dir is not empty! '
                        'Select another folder '
                        'or delete existing dicom files')
    dicomreport = DicomReport(root_folder, getpass.getuser())

    if not os.path.exists(report_folder):
        os.mkdir(report_folder)

    dicomreport.writereport(report_folder)

    if loris_folder:
        if not os.path.exists(loris_folder):
            try:
                os.mkdir(loris_folder)
            except OSError:
                raise OSError('Could not create LORIS output folder')
        dicomreport.reorganizefiles(loris_folder)


@main.command()
@click.option('--max_levels', type=int, default=10, show_default=True,
              help='Max unique values of a text variable \
                    that below that will be infered as nominal \
                    when no dataset metadata (schema) is provided')
@click.option('--sample_rows', type=int, default=100, show_default=True,
              help='Number rows that are going to be used as sample \
                    for infering the dataset metadata (schema) when \
                    metadata file is not provided')
@click.argument('input_csv', type=click.Path(exists=True))
@click.argument('output_json', type=click.Path())
def infercsv(input_csv, output_json, sample_rows, max_levels):
    dataset = QcTable(input_csv, schema=None)
    dataset.infer(limit=sample_rows, maxlevels=max_levels)
    dataset.schema.save(output_json)

    


if __name__ == '__main__':
    main()
