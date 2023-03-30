"""Function(s) for cleaning the data set(s)."""

import logging
from os.path import isfile

import geopandas as gpd
import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)


def clean_monthly_crime_data(
    crime_incidence_filepath,
    crime_type,
    year,
    month,
    columns_to_drop,
):
    """Function to clean the monthly crime data.

    Parameters:
    -----------
    crime_incidence_filepath: str
        The filepath to the raw monthly crime data.
    columns_to_drop: list
        List of columns to drop from the raw monthly crime data.
    crime_type: str
        The crime type to filter the data by.
    year: int
        The year of the crime data.
    month: int
        The month of the crime data.

    Returns:
    --------
        crime_data_monthly: pd.DataFrame
            The cleaned monthly crime data.

    """
    if isfile(crime_incidence_filepath):
        return _clean_monthly_crime_data(
            crime_incidence_filepath,
            columns_to_drop,
            crime_type,
        )

    logger.warning(f"Filepath doesn't exist: {crime_incidence_filepath}")
    logger.warning(f"Returning empty dataframe for year: {year} and month: {month}")

    return pd.DataFrame()


def _clean_monthly_crime_data(crime_incidence_filepath, columns_to_drop, crime_type):
    """Function to clean the monthly crime data.

    Parameters:
    -----------
    crime_incidence_filepath: str
        The filepath to the raw monthly crime data.
    columns_to_drop: list
        List of columns to drop from the raw monthly crime data.
    crime_type: str
        The crime type to filter the data by.

    Returns:
    --------
    crime_data_monthly: pd.DataFrame
        The cleaned monthly crime data.

    """
    crime_data_monthly = pd.read_csv(crime_incidence_filepath)

    ## remove unnecessary columns
    crime_data_monthly = crime_data_monthly.drop(
        columns=columns_to_drop,
    )

    ## remove rows columns that don't contain any latitude/longitude information
    crime_data_monthly = crime_data_monthly.dropna(
        subset=["Longitude", "Latitude"],
        how="all",
    )

    london_city_extent_mask = (
        (crime_data_monthly["Longitude"] > -0.53)
        & (crime_data_monthly["Longitude"] < 0.35)
        & (crime_data_monthly["Latitude"] > 51.275)
        & (crime_data_monthly["Latitude"] < 51.7)
    )

    crime_data_monthly = crime_data_monthly.loc[london_city_extent_mask]
    crime_data_monthly = crime_data_monthly.query(f"`Crime type` == '{crime_type}'")

    return crime_data_monthly


def convert_points_df_to_gdf(
    df,
    longitude_column_name="Longitude",
    latitude_column_name="Latitude",
    crs="EPSG:4326",
):
    """Function to convert a dataframe of points to a geodataframe.

    Parameters:
    -----------
    df: pd.DataFrame
        The dataframe containing the points.
    longitude_column_name: str
        The name of the column containing the longitude values.
    latitude_column_name: str
        The name of the column containing the latitude values.
    crs: str
        The coordinate reference system of the points.

    Returns:
    --------
    gpd.GeoDataFrame
        The geodataframe containing the points.

    """
    assert (
        longitude_column_name in df.columns
    ), f"{longitude_column_name}, not found in Dataframe columns."
    assert (
        latitude_column_name in df.columns
    ), f"{latitude_column_name}, not found in Dataframe columns."

    geometry = gpd.points_from_xy(
        x=df[longitude_column_name],
        y=df[latitude_column_name],
        crs=crs,
    )

    return gpd.GeoDataFrame(data=df, geometry=geometry)


def clean_regional_burglary_data(
    df,
    columns_to_keep,
    ID_column_name,
    crime_year="2019",
    crime_major_category="Burglary",
):
    """Function to clean the regional burglary data.

    Parameters:
    -----------
    df: pd.DataFrame
        The dataframe containing the regional burglary data.
    columns_to_keep: list
        The list of columns to keep from the dataframe.
    ID_column_name: str
        The name of the column containing the ID of the regions.
    crime_year: str
        The year of the crime data.
    crime_major_category: str
        The major category of the crime data.

    Returns:
    --------
    regional_cat_crime: pd.DataFrame
        The cleaned regional burglary data corresponding to the selected category.

    """
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
    """Function to convert a dataframe of regions to a geodataframe.

    Parameters:
    -----------
    df: pd.DataFrame
        The dataframe containing the regions.
    region_gdf: gpd.GeoDataFrame
        The geodataframe containing the regions.
    common_column_mapper: dict
        The dictionary containing the mapping between the dataframe and geodataframe column names.
    crs: str
        The coordinate reference system of the regions.

    Returns:
    --------
    gpd.GeoDataFrame
        The geodataframe containing the regions.

    """
    if crs is None:
        crs = region_gdf.crs

    # create gdf
    # rename gdf column to df column name
    region_gdf = region_gdf.rename(
        columns={common_column_mapper["gdf"]: common_column_mapper["df"]},
    )

    region_gdf = region_gdf.merge(df, on=common_column_mapper["df"], how="outer")
    region_gdf = region_gdf.fillna(0)

    region_gdf = region_gdf.to_crs(crs)

    return region_gdf


def aggregate_regional_level_data(
    lower_level_gdf,
    upper_level_gdf,
    ID_column_name,
    crs,
    weights_dict=None,
):
    """Function to aggregate regional level data to a lower level.

    Parameters:
    -----------
    lower_level_gdf: gpd.GeoDataFrame
        The geodataframe containing the lower level regions.
    upper_level_gdf: gpd.GeoDataFrame
        The geodataframe containing the upper level regions.
    ID_column_name: str
        The name of the column containing the ID of the regions.
    crs: str
        The coordinate reference system of the regions.
    weights_dict: dict
        The dictionary containing the weights to be used for aggregation.

    Returns:
    --------
    agg_gdf_groups: pd.DataFrame
        The aggregated data.

    """
    if lower_level_gdf.crs != upper_level_gdf.crs:
        lower_level_gdf = lower_level_gdf.to_crs(crs)
        upper_level_gdf = upper_level_gdf.to_crs(crs)

    # aggregating to ward level
    joined_gdf = upper_level_gdf.sjoin(lower_level_gdf, how="left")
    agg_gdf_groups = joined_gdf.groupby(ID_column_name)

    if weights_dict is not None:
        assert type(weights_dict) == dict, "weights_dict must be a dictionary."
        assert all(
            col in joined_gdf.columns for col in weights_dict["values_col"]
        ), "All specified columns in weights_dict 'values_col' not found in GeoDataFrame columns."

        assert (
            weights_dict["weights_col"] in joined_gdf.columns
        ), f"{weights_dict['weights_col']} not found in joined_gdf columns."

        agg_gdf = agg_gdf_groups.apply(
            lambda x: pd.Series(
                np.average(
                    x[weights_dict["values_col"]],
                    weights=x[weights_dict["weights_col"]],
                    axis=0,
                ),
                weights_dict["values_col"],
            ),
        )

    else:
        agg_gdf = agg_gdf_groups.sum()

    agg_gdf = agg_gdf.reset_index()

    # adding the geometry column back
    agg_gdf = upper_level_gdf[[ID_column_name, "geometry"]].merge(
        agg_gdf,
        on=ID_column_name,
        how="outer",
    )

    return agg_gdf


def extract_lsoa_imd_data(imd_data, lsoa, columns_to_keep, ID_column_name="LSOA11CD"):
    """Function to extract the imd data for the lsoa.

    Parameters:
    -----------
    imd_data: pd.DataFrame
        The dataframe containing the imd data.
    lsoa: pd.DataFrame
        The dataframe containing the lsoa data.
    columns_to_keep: list
        The list of columns to keep.
    ID_column_name: str
        The name of the column containing the ID of the regions.

    Returns:
    --------
    imd_lsoa: pd.DataFrame
        The imd data for the lsoa.

    """
    imd_lsoa = imd_data[imd_data["lsoa11cd"].isin(lsoa[ID_column_name])].reset_index(
        drop=True,
    )
    imd_lsoa = imd_lsoa[columns_to_keep]

    return imd_lsoa


def dissolve_gdf_polygons(gdf, dissolve_name, dissolve_key=None):
    """Function to dissolve polygons in a geodataframe.

    Parameters:
    -----------
    gdf: gpd.GeoDataFrame
        The geodataframe containing the polygons.
    dissolve_name: str
        The name of the dissolved polygon.
    dissolve_key: str
        The name of the column to use for dissolving.

    Returns:
    --------
    gdf_dissolved: gpd.GeoDataFrame
        The geodataframe containing the dissolved polygon.

    """
    if dissolve_key is None:

        gdf["dissolve_key"] = "dissolve"

    gdf_dissolved = gdf.dissolve(by="dissolve_key")
    gdf_dissolved.loc[:, "NAME"] = dissolve_name

    return gdf_dissolved
