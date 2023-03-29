"""Function(s) for cleaning the data set(s)."""

import logging
from os.path import isfile

import pandas as pd
import numpy as np
import geopandas as gpd

logger = logging.getLogger(__name__)

def clean_monthly_crime_data(crime_incidence_filepath, crime_type, year, month, columns_to_drop):

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
        return _clean_monthly_crime_data(
            crime_incidence_filepath, columns_to_drop, crime_type
        )

    logger.warning(f"Filepath doesn't exist: {crime_incidence_filepath}")
    logger.warning(f"Returning empty dataframe for year: {year} and month: {month}")

    return pd.DataFrame()

def _clean_monthly_crime_data(crime_incidence_filepath, columns_to_drop, crime_type):

    crime_data_monthly = pd.read_csv(crime_incidence_filepath)

    ## remove unnecessary columns
    crime_data_monthly = crime_data_monthly.drop(
        columns=columns_to_drop,
    )

    ## remove rows columns that don't contain any latitude/longitude information
    crime_data_monthly = crime_data_monthly.dropna(
        subset=["Longitude", "Latitude"], how="all",
    )

    london_city_extent_mask = ((crime_data_monthly["Longitude"] > -0.53) & (crime_data_monthly["Longitude"] < 0.35) & (crime_data_monthly["Latitude"] > 51.275) & (crime_data_monthly["Latitude"] < 51.7))

    crime_data_monthly = crime_data_monthly.loc[london_city_extent_mask]
    crime_data_monthly = crime_data_monthly.query(f"`Crime type` == '{crime_type}'")

    return crime_data_monthly

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

def aggregate_regional_level_data(lower_level_gdf, upper_level_gdf, ID_column_name, crs, weights_dict=None):

    if lower_level_gdf.crs != upper_level_gdf.crs:
        lower_level_gdf = lower_level_gdf.to_crs(crs)
        upper_level_gdf = upper_level_gdf.to_crs(crs)

    # aggregating to ward level
    joined_gdf = upper_level_gdf.sjoin(lower_level_gdf, how="left")
    agg_gdf_groups = joined_gdf.groupby(ID_column_name)

    if weights_dict is not None:
        assert type(weights_dict) == dict, "weights_dict must be a dictionary."
        # assert weights_dict["values_col"] in joined_gdf.columns, f"{weights_dict['values_col']} not found in joined_gdf columns."
        # assert weights_dict["weights_col"] in joined_gdf.columns, f"{weights_dict['weights_col']} not found in joined_gdf columns."
        assert all(
            col in joined_gdf.columns for col in weights_dict["values_col"]
        ), "All specified columns in weights_dict 'values_col' not found in GeoDataFrame columns."

        assert weights_dict["weights_col"] in joined_gdf.columns, f"{weights_dict['weights_col']} not found in joined_gdf columns."
        
        agg_gdf = agg_gdf_groups.apply(lambda x: pd.Series(np.average(x[weights_dict["values_col"]], weights=x[weights_dict["weights_col"]], axis=0), weights_dict["values_col"]))

    else:
        agg_gdf = agg_gdf_groups.sum()

    agg_gdf = agg_gdf.reset_index()

    # adding the geometry column back
    agg_gdf = upper_level_gdf[[ID_column_name, "geometry"]].merge(agg_gdf, on=ID_column_name, how="outer")

    return agg_gdf

def extract_lsoa_imd_data(imd_data, lsoa, columns_to_keep, ID_column_name="LSOA11CD"):
    
    imd_lsoa = imd_data[imd_data["lsoa11cd"].isin(lsoa[ID_column_name])].reset_index(drop=True)
    imd_lsoa = imd_lsoa[columns_to_keep]

    return imd_lsoa
