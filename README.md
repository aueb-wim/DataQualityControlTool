![AUEB](https://img.shields.io/badge/AUEB-RC-red.svg) [![Codacy Badge](https://api.codacy.com/project/badge/Grade/c08a182fec11456a8ba98ddeedb9ed4f)](https://www.codacy.com/app/iosifsp/QCtool?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=aueb-wim/QCtool&amp;utm_campaign=Badge_Grade) ![License](https://img.shields.io/badge/license-Apache--2.0-blue.svg)

# HBP-MIP Data Quality Control Tool

This tool is a component developed for the [Human Brain Project Medical Informatics Platform](https://www.humanbrainproject.eu/en/medicine/medical-informatics-platform/) (HBP-MIP). The main purpose of this tool is to produce statistical report of a given dataset and its variables (tabular dataset profiling) and propose value corrections for problematic data-entries. Also, the tool has the ability to extract and export meta-data headers of a set of DICOM MRIs.

## Installing / Getting started

### Prerequisites

Required installed packages for Debian based distros

-   python3, python3-pip, python3-tk
-   latexmk
-   texlive-latex-extra

```shell
sudo apt-get update
sudo apt-get install python3 python3-pip latexmk texlive-latex-extra
```

The above code installs the python3 and the minimum packages for a LaTex compiler. Alternative the `texlive-full` package can be installed instead of `latexmk` and `latexlive-latex-extra`.  

Required installed software for Windows

-   [python version 3](https://www.python.org/downloads/)

-   LaTex compiler installed
  -   [MiKTeX](https://miktex.org/download)
  -   [TeXstudio](https://www.texstudio.org/)
-   [Perl](https://www.perl.org/get.html)

### Installation

In a terminal we run

```shell
git clone https://github.com/aueb-wim/DataQualityControlTool.git
cd DataQualityControlTool
sh install.sh
```

## Usage

**Command Line Interface**
For profiling a csv dataset:

``` shell 
$ qctool csv --input_csv [dataset csv path] --meta_csv [metadata csv path] --col_val [metadata column name for variable codes/names] --col_type [metadata column name for variable types] (--readable) (--pdf)
```

first positional argument can take two flags `csv` or `dicom`. Here we use `csv` because the dataset is in csv format. 
`--readable` is an option if we want the reports csv files to have more descriptive column names.
`--pdf` is an option if we want to produce a report in pdf format. 
`col_val` and `col_type` are obligatory. They referred to column names of the metadata csv. The `col_val` is the name of the column that contains the variables codes used as columns in the datatset csv and the `col_type` is the name of the column in metadata csv that contains the variables types. 

At  the moment the tool needs the metadata file to detect the nominal variables. So, the `col_type` column must be filled with the value `nominal` (is not case sensitive)  for the categorical variables in order to work properly. Other types like `int`, `float`, `text`, `numerical`, `date` are not taken into account at the moment. 

After the execution, three files will be produced:

-   a csv file <dataset_file> + ‘_dataset_report.csv’ containing the Statistical Report of the given dataset.
-   a csv file <dataset_file> + ‘_report.csv’ containing the Statistical Reports of the variables of the given dataset.
-   a pdf or LaTex file <dataset_file>+’_report’ containg the above two reports in a readable format.

For profiling a dicom dataset:

``` shell
$ qctool dicom --root_folder [folder with dicoms] --report_folder [dicom report folderpath]
```

`--root_folder` is the root folder where the DICOM dataset is stored. It is assumed that each subfolder corresponds to one patient.
`--report_folder` is the folder where the report files will be placed. If the folder does not exist, the tool will create it.

The tool, depending of the results, creates the csv files:

-   validsequences.csv
-   invalidsequences.csv
-   invaliddicoms.csv
-   notprocessed.csv

### validsequences.csv

If there are valid sequences then the tool will create this csv file. A sequence is 'valid' if it meets the minimum requirements found [here](https://hbpmedical.github.io/deployment/data/). This file contains all the valid MRI sequences that found in given DICOM folder with the following headers discribing each sequence:

`PatientID`, `StudyID`, `SeriesDescription`, `SeriesNumber`, `ImageOrientation`, `SamplesPerPixel`, `Rows`, `Columns`,
`PixelSpacing`, `BitsAllocated`, `BitsStored`, `HighBit`, `AcquisitionDate`, `SeriesDate`, `PatientAge`, `PatientBirthDate`,
`MagneticFieldStrength`, `PatientSex`, `Manufacturer`, `ManufacturerModelName`, `InstitutionName`, `StudyDescription`,
`SliceThickness`, `RepetitionTime`, `EchoTime`, `SpacingBetweenSlices`, `NumberOfPhaseEncodingSteps`, `EchoTrainLength`,
`PercentPhaseFieldOfView`, `PixelBandwidth`, `FlipAngle`, `PercentSampling`, `EchoNumbers`

The values of those sequence tags are dirived from the headers in the  dicom files - more specifically, the value of a sequence tag is the most frequent value of this particular tag found in the sequence's dicom files.

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

-   `MissingTags` is a list of the missing mandatory DICOM tags.

### notprocessed.csv

If in the given root folder are some files that the QC tool can not process (not dicom files, corrupted dicom files etc), the tool will create this csv file with the following headers describing the location of those files:

`Folder`, `File`

### GUI

We run `qctoolgui`
See docs/quickguide.docx for further instructions.

## Features

-   Creates a statistical report for the dataset and its variables 
-   Creates a report with meta-data tags (headers) of each sequence (3D MRI Image) in a DICOM dataset
-   Command Line Interface and GUI

## Versioning

We use [SemVer](http://semver.org/) for versioning.

## Authors

-   Iosif Spartalis - AUEB/RC Data Science Team

## License

This project is licensed under the Apache 2.0 License - see the [LICENSE](LICENSE) file for details

## Acknowledgements

This work is part of SP8 of the Human Brain Project (SGA2).

Special thanks to:

-   **Prof. Vasilis Vassalos** - Athens University of Economics and Business
-   **Kostis Karozos** - AUEB/RC Data Science Team, Ph.D candiate
-   **Jacek Manthey** - CHUV
