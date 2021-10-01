![AUEB](https://img.shields.io/badge/AUEB-RC-red.svg) [![Codacy Badge](https://api.codacy.com/project/badge/Grade/c08a182fec11456a8ba98ddeedb9ed4f)](https://www.codacy.com/app/iosifsp/QCtool?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=aueb-wim/DataQualityControlTool&amp;utm_campaign=Badge_Grade) ![License](https://img.shields.io/badge/license-Apache--2.0-blue.svg) [![Coverage Status](https://coveralls.io/repos/github/aueb-wim/DataQualityControlTool/badge.svg?branch=master)](https://coveralls.io/github/aueb-wim/DataQualityControlTool?branch=master)

# HBP-MIP Data Quality Control Tool

## Description 

![MIP DQCT logo](docs/img/dqctlogo_v2_100x55.png)

MIP Data Quality Control Tool (MIP-DQC Tool) is a software developed for the [Human Brain Project Medical Informatics Platform](https://www.humanbrainproject.eu/en/medicine/medical-informatics-platform/) (HBP-MIP) and it main perpose is to provide hospital personel an easy way to explore, validate and transform their data before uploading them into the MIP. MIP-DQC Tool has both, a Command Line Interface (CLI) and a Graphical User Interface (GUI) but only the latter one has the full set of tool's functionalities.

MIP-DQC Tool GUI version has the following functionalities:

1. Validating the hospital tabular (csv) data and producing report with validation results and some overall statistics about the data.
2. Data cleaning capability based on the previously performed validation results.
3. Inference of a dataset's schema and producing a schema file in [Frictionless json](https://frictionlessdata.io/) or MIP Data Catalogue's excel format.
4. Designing and performing schema mapping of an incoming hospital dataset to a certain Pathology's Common Data Element (CDE) schema.
5. Producing DICOM MRIs validation and statistical report based on their meta-data headers.

The tabular (csv) **data validation** functionality has the option of downloading pathologies CDE metadata directly from the [MIP Data Catalogue's API](datacatalogue.mip.ebrains.eu). Please note, this option **is not available in the CLI version**. 

The **schema mapping** functionality is performed by the [MIPMap](https://github.com/HBPMedical/MIPMap) engine packaged in a **Docker container** which runs in the background. Please note, this option **is not available in the CLI version**.

## Suported OS

- Linux (tested for Ubuntu)
- Windows 10 with WLS 2
- MacOS

Please refer to the [Installation Wiki Section](https://github.com/aueb-wim/DataQualityControlTool/wiki/Installation) for further details. 

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
