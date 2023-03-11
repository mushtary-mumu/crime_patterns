"""Function(s) for cleaning the data set(s)."""

import logging
from os.path import isfile

import pandas as pd
import geopandas as gpd

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

def convert_points_df_to_gdf(df, longitude_column_name="Longitude", latitude_column_name="Latitude", crs="EPSG:4326"):

    assert longitude_column_name in df.columns, f"{longitude_column_name}, not found in Dataframe columns."
    assert latitude_column_name in df.columns, f"{latitude_column_name}, not found in Dataframe columns."

    geometry = gpd.points_from_xy(x = df[longitude_column_name], y = df[latitude_column_name], crs=crs)

    return gpd.GeoDataFrame(data=df, geometry=geometry)

def clean_regional_burglary_data(df, columns_to_keep, ID_column_name, crime_year="2019", crime_major_category="Burglary"):

    ## Clean burglary data
    ## Select crime category
    regional_cat_crime = df.query(f"`Major Category` == '{crime_major_category}'")

    ## Select year
    month_columns = regional_cat_crime.filter(regex=crime_year).columns
    columns_to_keep = columns_to_keep + list(month_columns)
    regional_cat_crime = regional_cat_crime[columns_to_keep]

    regional_cat_crime = regional_cat_crime.groupby(by=ID_column_name).sum()

    ## Sum crime for whole year
    
    regional_cat_crime[f"{crime_year}_total"] = regional_cat_crime[month_columns].sum(1)
    
    return regional_cat_crime.reset_index()

def convert_region_df_to_gdf(df, region_gdf, common_column_mapper, crs=None):
        
    if crs is None: crs = region_gdf.crs

    # create gdf
    # rename gdf column to df column name
    region_gdf = region_gdf.rename(columns={common_column_mapper["gdf"]: common_column_mapper["df"]})

    region_gdf = region_gdf.merge(df, on=common_column_mapper["df"], how="outer") 
    region_gdf = region_gdf.fillna(0)

    region_gdf = region_gdf.to_crs(crs)

    return region_gdf

def aggregate_regional_level_data(lower_level_gdf, upper_level_gdf, ID_column_name):

    # aggregating to ward level
    agg_gdf = upper_level_gdf.sjoin(lower_level_gdf, how="left")
    agg_gdf = agg_gdf.groupby(ID_column_name).sum()
    agg_gdf = agg_gdf.reset_index()

    # adding the geometry column back
    agg_gdf = upper_level_gdf[[ID_column_name, "geometry"]].merge(agg_gdf, on=ID_column_name, how="outer")

    return agg_gdf