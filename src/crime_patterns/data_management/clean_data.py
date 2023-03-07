"""Function(s) for cleaning the data set(s)."""

import logging
from os.path import isfile

import pandas as pd

logger = logging.getLogger(__name__)

# def clean_data(data, data_info):
#     """Clean data set.

#     Information on data columns is stored in ``data_management/data_info.yaml``.

#     Args:
#         data (pandas.DataFrame): The data set.
#         data_info (dict): Information on data set stored in data_info.yaml. The
#             following keys can be accessed:
#             - 'outcome': Name of dependent variable column in data
#             - 'outcome_numerical': Name to be given to the numerical version of outcome
#             - 'columns_to_drop': Names of columns that are dropped in data cleaning step
#             - 'categorical_columns': Names of columns that are converted to categorical
#             - 'column_rename_mapping': Old and new names of columns to be renamend,
#                 stored in a dictionary with design: {'old_name': 'new_name'}
#             - 'url': URL to data set

#     Returns:
#         pandas.DataFrame: The cleaned data set.

#     """
#     for cat_col in data_info["categorical_columns"]:




def clean_monthly_crime_data(crime_incidence_filepath, year, month, data_info):
    """Loads and cleans monthly crime data

    Args:
        crime_incidence_filepath (_type_): _description_
        year (_type_): _description_
        month (_type_): _description_
        data_info (_type_): _description_

    Returns:
        _type_: _description_
    """
    if isfile(crime_incidence_filepath):

        crime_data_monthly = pd.read_csv(crime_incidence_filepath)

        ## remove unnecessary columns
        crime_data_monthly = crime_data_monthly.drop(
            columns=data_info["columns_to_drop"],
        )

        ## remove rows columns that don't contain any latitude/longitude information
        crime_data_monthly = crime_data_monthly.dropna(
            subset=["Longitude", "Latitude"], how="all",
        )

        return crime_data_monthly

    else:
        logger.warning(f"Filepath doesn't exist: {crime_incidence_filepath}")
        logger.warning(f"Returning empty dataframe for year: {year} and month: {month}")
        return pd.DataFrame()
