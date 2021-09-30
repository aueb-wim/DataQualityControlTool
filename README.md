![AUEB](https://img.shields.io/badge/AUEB-RC-red.svg) [![Codacy Badge](https://api.codacy.com/project/badge/Grade/c08a182fec11456a8ba98ddeedb9ed4f)](https://www.codacy.com/app/iosifsp/QCtool?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=aueb-wim/DataQualityControlTool&amp;utm_campaign=Badge_Grade) ![License](https://img.shields.io/badge/license-Apache--2.0-blue.svg) [![Coverage Status](https://coveralls.io/repos/github/aueb-wim/DataQualityControlTool/badge.svg?branch=master)](https://coveralls.io/github/aueb-wim/DataQualityControlTool?branch=master)

# HBP-MIP Data Quality Control Tool

## Description 

![MIP DQCT logo](docs/img/dqctlogo_v2_100x55.png)

This tool is a component developed for the [Human Brain Project Medical Informatics Platform](https://www.humanbrainproject.eu/en/medicine/medical-informatics-platform/) (HBP-MIP) and it main perpose is to provide hospital personel an easy way to explore, validate and transform their data before uploading them into the MIP.
The tool has the following functionalities:

1. Validating the hospital EHR data and producing report with validation results and some overall statistics about the data.
2. Data cleaning capability.
3. Inference of a dataset's schema and producing a schema file in [Frictionless json](https://frictionlessdata.io/) or Data Catalogue's excel format.
4. Designing and performing schema mapping of an incoming hospital dataset to a certain Pathology's Common Data Element (CDE) schema.
5. Producing DICOM MRIs validation and statistical report based on their meta-data headers.


## Usage

### Command Line Interface

For profiling/validating a csv dataset:

``` shell
Usage: qctool csv <options> <csv file> <schema json>

  This command produces a validation report for <csv file>.

  The report file is stored in the same folder where <csv file> is located.

  <schema json> file MUST be compliant with frirctionless   data table-
  schema specs(https://specs.frictionlessdata.io/table-schema/) or   with
  Data Catalogue json format.

Options:
  --clean                 Flag for performing data cleaning.The cleaned file will 
                          be saved in the report folder.

  -m, --metadata [dc|qc]  Select "dc" for Data Catalogue spec json
                          or "qc" for frictionless spec json.

  -r, --report [xls|pdf]  Select the report file format.
  -o, --outlier FLOAT     outlier threshold in standard deviations.
  --help                  Show this message and exit.
  ```

**outlier threshold** input field is related with the outlier detection for numerical variables of the incoming dataset. The way that the Data Quality Control tool handles the outlier detection of a certain numerical variable, is that first calculates the **mean** and the **standard deviation** based on the valid values of that column and then calculates the upper and the lower limit by the formula: `upper_limit = mean + outlier threshold * standard deviation`, `lower_limit = mean - outlier threshold * standard deviation`. If any value is outside those limits then it is considered as an outlier. 

The report file will be saved in the folder where the incoming dataset file is located.

#### Data Cleaning

After reviewing the **Data Validation** report created in the previous step (Please refer to the **Data Validation Report** wiki section for further details), we can proceed with the data cleaning operation. The cleaned dataset file will be saved in same folder where the incoming dataset is located by using the original dataset name with the addition of the suffix '_corrected'.

For infering a dataset's schema:

```shell
Usage: qctool infercsv <options> <csv file>

  This command infers the schema of the <csv file> it and stored in <output
  file>.

  The <output file> either a json file following the frictionless data
  specs(https://specs.frictionlessdata.io/table-schema/) or an xlsx file
  following MIP Data Catalogue's format.

Options:
  --max_levels INTEGER         Max unique values of a text variable
                               that below that will be infered as nominal
                               [default: 10]

  --sample_rows INTEGER        Number rows that are going to be used as sample
                               for infering the dataset metadata (schema)
                               [default: 100]

  --schema_spec [dc|qc]        Select "dc" for Data Catalogue spec xlsx file
                               or "qc" for frictionless spec json.

  --cde_file PATH              CDE dictionary Excel file (xlsx)
  -t, --threshold FLOAT RANGE  CDE similarity threshold.
  --help                       Show this message and exit.
```

 The schema could be saved in two formats:

1. Frictionless spec json
2. Data Catalogue's spec Excel (xlsx) file, that can be used for creating a new CDE pathology version.

In the infer option section, we give the number of rows that the tool will based on for the schema inference. Also, we declare the maximum number of categories that a `nominal` MIPType variable can have.

If we choose the Data Catalogue's excel as an output, the tool offers the option of suggesting CDE variables for each column of the incoming dataset. This option is possible, only when a CDE dictionary is provided. This dictionary is an excel file that contains information for all the CDE variables that are included or will be included in the MIP (this dictionary will be available in the Data Catalogue in the near future). The tool calculates a similarity measure for each column based on the column name similarity (80%) and the value range similarity (20%). The similarity measure takes values between 0 and 1. With the option **similarity threshold** we can define the minimum similarity measure between an incoming column and a CDE variable that need to be met in order the tool to suggest that CDE variable as a possible correspondence. The tool stores those CDE suggestions in the excel file in the column named **CDE** and  also stores the corresponding concept path under the column **conceptPath**.

For profiling a dicom dataset:

``` shell
Usage: qctool dicom <options> <dicom folder> <report folder>
```

`<dicom folder>` is the root folder where all DICOM files are stored. It is assumed that each subfolder corresponds to one patient.

`<report folder>` is the folder where the report files will be placed. If the folder does not exist, the tool will create it.

Options: 

`--loris_folder`  folder path where the dcm files are reorganized for LORIS pipeline

For the LORIS pipeline the dcm files are reorganized and stored in a folder structure `<loris_folder>/<patientid>/<patientid_visitcount>`.
All the dcm sequence files that belong to the same scanning session (visit) are stored in the common folder `<patientid_visitcount>`.

The tool creates in the `<report folder>`, a pdf report file (`dicom_report.pdf`) and, depending of the results, also creates the following csv files :

-   validsequences.csv
-   invalidsequences.csv
-   invaliddicoms.csv
-   notprocessed.csv
-   mri_visits.csv

The above files are created even if no valid/invalid sequences/dicoms files have been found. In such case, the files will be empty.

### validsequences.csv

If there are valid sequences then the tool will create this csv file. A sequence is 'valid' if it meets the minimum requirements found [here](https://hbpmedical.github.io/deployment/data/). This file contains all the valid MRI sequences that found in given DICOM folder with the following headers discribing each sequence:

`PatientID`, `StudyID`, `SeriesNumber`, `SeriesDescription`, `SeriesDate`

The value of the sequence tags `SeriesDescription` and `SeriesDate` are dirived from the headers in the  dicom files - more specifically, the value of a sequence tag is the most frequent value of this particular tag found in the sequence's dicom files.

### invalidsequences.csv

If there are invalid sequences the tool will create this csv file with the following headers:

`PatientID`, `StudyID`, `SeriesNumber`, `Slices`, `Invalid_dicoms`, `SeriesDescription`, `Error1`, `Error2`, `Error3`, `Error4`, `Error5`, `Error6`

-   `Slices` is the number of dicom files that the current sequence is consist of (sum of valid and invalid dicoms).
-   `Invilid_dicoms` is the number of invalid dicom files the current sequence.  
-   `Error1` - `Error6` is an error description that explains the reason why the sequence is characterized as 'invalid'

### invaliddicoms.csv

If a dicom file does not have at least one of the mandatory tags as described in the MIP specification found [here](https://hbpmedical.github.io/deployment/data/), then it will be characterized as 'invald'.
If there are invalid dicoms in the DICOM dataset, the tool will create this csv file with the following headers:

`Folder`, `File`, `PatientID`, `StudyID`, `SeriesNumber`, `InstanceNumber`, `MissingTags`

- `MissingTags` is a list of the missing mandatory DICOM tags.

### notprocessed.csv

If in the given root folder are some files that the QC tool can not process (not dicom files, corrupted dicom files etc), the tool will create this csv file with the following headers describing the location of those files:

`Folder`, `File`

### mri_visits.csv

This file contains MRI visit information for each patient. This file is necessary for the HBP MIP DataFactory's [Step3_B](https://github.com/HBPMedical/ehr-datafactory-template#importing-the-volumetric-brain-features-into-the-i2b2-capture-database) and it has the following headers:

`PATIENT_ID`, `VISIT_ID`, `VISIT_DATE`

### GUI

We run `qctoolgui`

See **GUI User Guide** section in the wiki for further usage details. 

## Versioning

We use [SemVer](http://semver.org/) for versioning.

## Authors

- Iosif Spartalis - AUEB/RC Data Science Team @iosifsp

## License

This project is licensed under the Apache 2.0 License - see the [LICENSE](LICENSE) file for details

## Acknowledgements

This work is part of SP8 of the Human Brain Project (SGA2).

The app logo is based on a design by the user `Eucalyp`, from [Flaticon website](https://www.flaticon.com/)

Special thanks to:

-   **Prof. Vasilis Vassalos** - Athens University of Economics and Business
-   **Kostis Karozos** - AUEB/RC Data Science Team, Ph.D candidate @Kostis-K
-   **Abu-Nawwas Laith** - CHUV @lanawwas
-   **Jacek Manthey** - CHUV
