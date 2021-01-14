# cli.py
""" Command Line Interface for MIP Quality Control Tool
"""
import os
import click
import getpass
import json

from mipqctool.dicomreport import DicomReport
from mipqctool.tablereport import TableReport
from mipqctool.inferschema import InferSchema
from mipqctool.qcfrictionless import QcTable, QcSchema, FrictionlessFromDC, CdeDict
from mipqctool.config import LOGGER

DIR_PATH = os.path.dirname(os.path.abspath(__file__))


@click.group()
def main():
    pass


@main.command(options_metavar='<options>')
@click.argument('input_csv', type=click.Path(exists=True), metavar='<csv file>')
@click.argument('schema_json', type=click.Path(exists=True), metavar='<schema json>')
#@click.option('--col_id', type=int, required=True, default=1, show_default=True,
#              help='Column number that holds id values (primary key).')
@click.option('--clean', is_flag=True,
              help='Flag for performing data cleaning.The cleaned file will \
                    be saved in the report folder.')
@click.option('-m', '--metadata', type=click.Choice(['dc', 'qc']), default='dc',
              help='Select "dc" for Data Catalogue spec json \
                    or "qc" for frictionless spec json.')
@click.option('-r', '--report', type=click.Choice(['xls','pdf']), default='xls',
              help='Select the report file format.')
@click.option('-o', '--outlier', type=click.FLOAT, default=3,
              help='outlier threshold in standard deviations.')
def csv(input_csv, schema_json, clean,
        metadata, report, outlier):
    """This command produces a validation report for <csv file>.

    The report file is stored in the same folder where <csv file> is located.
    
    <schema json> file MUST be compliant with frirctionless
      data table-schema specs(https://specs.frictionlessdata.io/table-schema/) or
      with Data Catalogue json format.
    """
    filename = os.path.basename(input_csv)
    # Get the path of the csv file
    path = os.path.dirname(os.path.abspath(input_csv))

    dataset_name = os.path.splitext(filename)[0]
    pdfreportfile = os.path.join(path, dataset_name + '_report.pdf')
    xlsxreportfile = os.path.join(path, dataset_name + '_report.xlsx')
    correctedcsvfile = os.path.join(path, dataset_name + '_corrected.csv')
    
    # read the json file with the csv schema
    with open(schema_json) as json_file:
        dict_schema = json.load(json_file)

    # check metadata json type is Data Catalogue specs 
    if metadata=='dc':
        LOGGER.info('Transating from Data Catalogue to Frictionless json format...')
        dict_schema = FrictionlessFromDC(dict_schema).qcdescriptor
    
    schema = QcSchema(dict_schema)
    dataset = QcTable(input_csv, schema=schema)

    datasetreport = TableReport(dataset, threshold=outlier)

    # Apply data cleaning corrections?
    if clean:
        datasetreport.apply_corrections()
        datasetreport.save_corrected(correctedcsvfile)

    if datasetreport.isvalid:
        LOGGER.info('The dataset has is valid.')
    else:
        LOGGER.info('CAUTION! The dataset is invalid!')

    # export the report 
    if report == 'pdf':
        datasetreport.printpdf(pdfreportfile)
    elif report == 'xls':
        datasetreport.printexcel(xlsxreportfile)


@main.command(options_metavar='<options>')
@click.argument('dicom_folder', type=click.Path(exists=True), metavar='<dicom folder>')
@click.argument('report_folder', type=click.Path(), metavar='<report folder>')
@click.option('--loris_folder', type=click.Path(), metavar='<loris input folder>',
              help='LORIS input folder where the dcm files in <dicom folder> will be reorganized')
def dicom(ctx, dicom_folder, report_folder, loris_folder=None):
    """This command produces a validation report for MRIs in <dicom folder>.

    All MRI dcm files belogning to the same Patient MUST
    be in the same subfolder in <dicom folder>.
    
    The validation report files are stored in <report folder>.
    """
    if loris_folder and len(os.listdir(loris_folder)) != 0:
        raise Exception('LORIS output dir is not empty! '
                        'Select another folder '
                        'or delete existing dicom files')
    dicomreport = DicomReport(dicom_folder, getpass.getuser())

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


@main.command(options_metavar='<options>')
@click.option('--max_levels', type=int, default=10, show_default=True,
              help='Max unique values of a text variable \
                    that below that will be infered as nominal')
@click.option('--sample_rows', type=int, default=100, show_default=True,
              help='Number rows that are going to be used as sample \
                    for infering the dataset metadata (schema)')
@click.option('--schema_spec', type=click.Choice(['dc', 'qc']), default='dc',
              help='Select "dc" for Data Catalogue spec xlsx file \
                    or "qc" for frictionless spec json.')
@click.option('--cde_file', type=click.Path(exists=True),
              help='CDE dictionary Excel file (xlsx)')
@click.option('-t', '--threshold', type=click.FloatRange(min=0.0, max=1.0), default=0.6,
              help='CDE similarity threshold.')
@click.argument('input_csv', type=click.Path(exists=True), metavar='<csv file>')
def infercsv(input_csv, schema_spec, sample_rows, max_levels, threshold, cde_file=None):
    """This command infers the schema of the <csv file> it and stored in <output file>.

    The <output file> either a json file following the frictionless data specs(https://specs.frictionlessdata.io/table-schema/)
    or an xlsx file following MIP Data Catalogue's format.
    
    """
    filename = os.path.basename(input_csv)
    # Get the path of the csv file
    path = os.path.dirname(os.path.abspath(input_csv))

    dataset_name = os.path.splitext(filename)[0]
    qcjsonfile = os.path.join(path, dataset_name + '_qcschema.json')
    dcxlsxfile = os.path.join(path, dataset_name + '_dcschema.xlsx')

    dataset = QcTable(input_csv, schema=None)
    # Is cde dictionary file available?
    if cde_file:
        cde_dict = CdeDict(cde_file)
    else:
        cde_dict = None

    infer = InferSchema(dataset, dataset_name, sample_rows, max_levels, cde_dict)
    
    # suggest cdes and concept paths if cde dictionary is available
    if cde_dict:
        infer.suggest_cdes(threshold=threshold)

    if schema_spec == 'dc':
        infer.export2excel(dcxlsxfile)
    elif schema_spec == 'qc':
        infer.expoct2qcjson(qcjsonfile)


if __name__ == '__main__':
    main()
