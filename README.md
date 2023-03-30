# Crime Data Mapping and Spatial Regression

| main                                                                                                                                                                                    | develop                                                                                                                                                                                    |
| --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| [![main](https://github.com/mushtary-mumu/crime_patterns/actions/workflows/main.yml/badge.svg?branch=main)](https://github.com/mushtary-mumu/crime_patterns/actions/workflows/main.yml) | [![main](https://github.com/mushtary-mumu/crime_patterns/actions/workflows/main.yml/badge.svg?branch=develop)](https://github.com/mushtary-mumu/crime_patterns/actions/workflows/main.yml) |

## Project Title

> ## **Burglary Crime Patterns and its Driving Factors in the City of London**
>
> #### *EPP for Economists Final Project, University of Bonn WS 22/23*
>
> <img src="burglary_hotspots.png" width="500" height="400">

> #### Author
>
> **Mudabbira Mushtary** *Student of M.Sc. Economics* University of Bonn © 2022-2023

## Project Description

This project analyzes the burglary crime patterns in the city of London, England's
highest crime-rate city. As a first step the crime data from the
[City of London Police](https://data.police.uk/data/) and the
[Metropoliton Police Service](https://data.police.uk/data/) along with the
[English indices of deprivation 2019](https://www.gov.uk/government/statistics/english-indices-of-deprivation-2019)
are downloaded, extracted and cleaned. The next step involves a series of analysis on
the burglary crime data and the indices of deprivation in order to answer certain
research questions as listed below:

- Spatial Point Pattern Analysis
  - Where are the burglary crime incidents located in the City of London?
  - Are the burglary incidents clustered in certain areas?
  - Where are the burglary hotspots located?
- Spatial Autocorrelation
  - Q1
  - Q2
  - Q3
- Spatial Regression.
  - Q1
  - Q2
  - Q3

The primary goal of the project is placed on reproducibility of the results by utilizing
the research-software programming best-practices learned in the course "Effective
Programming Practices for Economists" taught at the University of Bonn.

## Getting started

For a local machine to run this project, it needs to have a Python and LaTeX
distribution pre-installed. The project was tested primarily on Windows 11 operating system, but should also work on Linux and Mac OS.

The project environment includes all the dependencies needed to run the project.

To run this project on a local machine:

- after cloning the repo, open a terminal in the root directory of the project and
  create and activate the environment by typing:

```console
conda env create -f environment.yml
conda activate crime_patterns
```

- To generate the output files that will be stored in `bld` folder, type `pytask` in the
  root directory of your terminal.

```console
pytask
```

> **Note**
> When pytask is run for the first time, it will download and unzip a decent amount of raw data files onto the local machine. This will take a while, but will only happen once. Subsequent runs of pytask will be much faster. The downloaded raw data files are stored in `src/crime_patterns/data` folder. It is therefore recommended to have at least 5 GB of free space on the local machine.

- To run the tests stored in the `tests` folder, type `pytest` in the
  root directory of your terminal.

```console
pytest --cov=crime_patterns tests/
```

## Project structure

`src` directory includes all the necessary code used in the analysis. To navigate
through the folders, the workflow is decomposed as follows:

- `src/crime_patterns/data_management` contains the code to clean and format the data
  for the subsequent analysis.
- `src/crime_patterns/analysis` contains code for all the analysis mentioned above,
  intuitively named in separte files.
- `src/crime_patterns/final` includes code to generate final tables and figures.
- `src/crime_patterns/paper` contains the tasks to generate the final
  project presentation.
- `paper/` contains the LaTeX files corresponding to the final project
  presentation.

<!--- - `documentation` generates pdf and html files for the documentaion of the project code. --->

- `tests/` contains the tests functions that test the code stored in `src/`.

## Credits

This project was created with [cookiecutter](https://github.com/audreyr/cookiecutter)
and the
[econ-project-templates](https://github.com/OpenSourceEconomics/econ-project-templates).
