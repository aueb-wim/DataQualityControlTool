![AUEB](https://img.shields.io/badge/AUEB-RC-red.svg) [![Codacy Badge](https://api.codacy.com/project/badge/Grade/c08a182fec11456a8ba98ddeedb9ed4f)](https://www.codacy.com/app/iosifsp/QCtool?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=aueb-wim/QCtool&amp;utm_campaign=Badge_Grade) ![License](https://img.shields.io/badge/license-Apache--2.0-blue.svg)

# HBP-MIP Data Quality Control Tool

This tool is a component developed for the [Human Brain Project Medical Informatics Platform](https://www.humanbrainproject.eu/en/medicine/medical-informatics-platform/) (HBP-MIP). The main perpose of this tool is to produce statistical report of a given dataset and its variables (tabular dataset profiling) and propose value corrections for problematic data-entries. Also, the tool has the ability to extract and export meta-data headers of a set of DICOM MRIs.
## Installing / Getting started
### Prerequisites
Required installed packages for Debian based distros
-   python3, python3-pip
-   latexmk 
-   texlive-latex-extra

```shell
$ sudo apt-get update
$ sudo apt-get install python3 python3-pip latexmk texlive-latex-extra
```
The above code installs the python3 and the minimum packages for a LaTex compiler. Alternative the `texlive-full` package can be installed instead of `latexmk` and `latexlive-latex-extra`.  

Requiered installed software for Windows
-   [python version 3](https://www.python.org/downloads/)
-   LaTex compiler installed
  -   [MiKTeX](https://miktex.org/download)
  -   [TeXstudio](https://www.texstudio.org/)
-   [Perl](https://www.perl.org/get.html)

### Installation
In a terminal we run
```shell
$ git clone https://github.com/aueb-wim/DataQualityControlTool.git
$ cd DataQualityControlTool
$ sh install.sh
```

## Use
**Command Line Interface**
For profiling a csv dataset:
``` shell 
$ qctool -m csv --input_csv [dataset csv path] --meta_csv [metadata csv path] --col_val [metadata column name for variable codes/names] --col_type [metadata column name for variable types] (--readable) (--pdf)
```
`-m` or `--mode` can take two flags `csv` or `dicom`. Here we use `csv` because the dataset is in csv format. 
`--readable` is a flag if we want the reports csv files to have more descriptive column names. 
`--pdf` is a flag if we want to produce a report in pdf format
`col_val` and `col_type` are obligatory. They are referred to columns names of the metadata csv. The `col_val` is the name of the column that contains the variables codes used as columns in the datatset csv and the `col_type` is the name of the column in metadata csv that contains the variables types. 

At  the moment the tool needs the metadata file to detect the nominal variables. So, the `col_type` column must be filled with the value `nominal` (is not case sensitive)  for the categorical variables in order to work properly. Other types like `int`, `float`, `text`, `numerical`, `date` are not taken into account at the moment. 

After the execution, three files will be produced:
-   a csv file <dataset_file> + ‘_dataset_report.csv’ containing the Statistical Report of the given dataset.
-   a csv file <dataset_file> + ‘_report.csv’ containing the Statistical Reports of the variables of the given dataset.
-   a pdf or LaTex file <dataset_file>+’_report’ containg the above two reports in a readable format.

For profiling a dicom dataset:
``` shell
$ qctool -m dicom --root_folder [folder with dicoms] --report_xls [path/to/report.xls]
```
The report is in excel format and contains the header information from all DICOM (dcm) files.

**GUI**
We run `qctoolgui`
See docs/quickguide.docx for furthe instructions. 

## Features
-   Creates a statistical report for the dataset and its variables 
-   Creates a report with the meta-data headers of a set of MRIs 
-   Command Line Interface and GUI 

## Versioning
We use [SemVer](http://semver.org/) for versioning.

## Authors
-   Iosif Spartalis - AUEB/RC Data Science Team

## License
This project is licensed under the Apache 2.0 License - see the [LICENSE](LICENSE) file for details

## Acknowledgements

This work is part of SP8 of the Human Brain Project (SGA2).
