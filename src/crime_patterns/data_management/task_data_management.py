"""Tasks for managing the data."""
#%%
import itertools
import os

import numpy as np
import pandas as pd
import geopandas as gpd
import pytask

import crime_patterns.config as config
import crime_patterns.data_management as dm
import crime_patterns.utilities as utils 

src = config.SRC
bld = config.BLD
data_raw = src / "data"
data_clean = bld / "python" / "data"

## TODO: consider moving some of the things to config.py or data_info.yml
data_info = utils.read_yaml(src / "data_management" / "data_info.yaml")
year = data_info["crime_year"]

months = ["%.2d" % i for i in np.arange(1, 13, 1)]
crime_data_filepaths_london_police = {
    f"{year}-{month}-london": os.path.join(data_raw / data_info['data_raw_dirs']["uk_crime_data_2019"], f"{year}-{month}", f"{year}-{month}-city-of-london-street.csv")
    for month in months
}

crime_data_filepaths_metropoliton_police = {
    f"{year}-{month}-metropoliton": os.path.join(data_raw / data_info['data_raw_dirs']["uk_crime_data_2019"], f"{year}-{month}", f"{year}-{month}-metropolitan-street.csv")
        for month in months
}
crime_data_filepaths = (
    crime_data_filepaths_london_police
    | crime_data_filepaths_metropoliton_police
)

#%%
@pytask.mark.depends_on(
    {
        "scripts": ["clean_data.py"],
        "data_info": src / "data_management" / "data_info.yaml",
        "london_ward_shp": data_raw / data_info['data_raw_dirs']["statistical_gis_boundaries_london"] / data_info['data_raw_dirs']["statistical_gis_boundaries_london"] / "ESRI" / "London_Ward.shp",
        "crime_data_filepaths": crime_data_filepaths,
    },
)
@pytask.mark.produces(
    {
        "greater_london_area": data_clean / "Greater_London_Area.shp",
        "cleaned_shp": data_clean / "city-of-london-burglaries-2019-cleaned.shp",
        "cleaned_csv": data_clean / "city-of-london-burglaries-2019-cleaned.csv",
    }
)
def task_clean_crime_incidences_data(depends_on, produces):

    """Clean the data (Python version)."""
    crime_data_monthly = [
        dm.clean_monthly_crime_data(
            crime_incidence_filepath=depends_on["crime_data_filepaths"][key],
            year=key.split("-")[0],
            month=key.split("-")[1],
            crime_type=data_info["crime_type"],
            columns_to_drop=data_info["uk_crime_data_2019_columns_to_drop"],
        )
        for key in depends_on["crime_data_filepaths"]
    ]
    crime_data_yearly = pd.concat(crime_data_monthly)

    ## Drop duplicate points
    crime_data_yearly = crime_data_yearly.drop_duplicates(subset=['Longitude', 'Latitude'], keep='first')

    # crime_data_yearly.to_csv(produces["cleaned_csv"], index=False)

    ## TODO: consider renaming columns that have more than 10 characters to avoid truncation
    crime_data_yearly_gdf = dm.convert_points_df_to_gdf(df = crime_data_yearly).to_crs(config.CRS)
    
    london_wards = gpd.read_file(depends_on["london_ward_shp"]).to_crs(config.CRS)
    london_wards["dissolve_key"] = "dissolve"
    london_ward_dissolved = london_wards.dissolve(by="dissolve_key")
    london_ward_dissolved.loc[:, "NAME"]  = "Greater London Area"
    london_ward_dissolved.to_file(filename=produces["greater_london_area"])
    
    crime_data_yearly_gdf = gpd.sjoin(crime_data_yearly_gdf, london_ward_dissolved, how='inner')
    crime_data_yearly_gdf.to_file(filename=produces["cleaned_shp"])
    crime_data_yearly_gdf.to_csv(produces["cleaned_csv"], index=False)

# %%
@pytask.mark.depends_on(
    {
        "scripts": ["clean_data.py"],
        "data_info": src / "data_management" / "data_info.yaml",
        "london_lsoa_shp": data_raw / data_info['data_raw_dirs']["statistical_gis_boundaries_london"] / data_info['data_raw_dirs']["statistical_gis_boundaries_london"] / "ESRI" / "LSOA_2011_London_gen_MHW.shp",
        "london_ward_shp": data_raw / data_info['data_raw_dirs']["statistical_gis_boundaries_london"] / data_info['data_raw_dirs']["statistical_gis_boundaries_london"] / "ESRI" / "London_Ward.shp",
        "lsoa_crime_data": data_raw / data_info['data_raw_dirs']["lsoa_level_crime"] / "MPS LSOA Level Crime (Historical).csv"
    },
)
@pytask.mark.produces(
    {
        "lsoa_crime_data_cleaned": data_clean / "MPS_LSOA_Level_burglary_2019.shp",
        "ward_crime_data_cleaned": data_clean / "MPS_Ward_Level_burglary_2019.shp",
    }
)
def task_prepare_ward_level_crime_data(depends_on, produces):

    common_column_mapper = {"df": "LSOA Code",
                            "gdf": "LSOA11CD"}

    ## load
    london_lsoa = gpd.read_file(depends_on["london_lsoa_shp"])
    london_wards = gpd.read_file(depends_on["london_ward_shp"])
    lsoa_crime_data = pd.read_csv(depends_on["lsoa_crime_data"])

    # TODO: move some input parameters to data_info.yaml
    mps_lsoa_burglary_2019 = dm.clean_regional_burglary_data(
                                                df = lsoa_crime_data,
                                                columns_to_keep = ['LSOA Code', 'LSOA Name', 'Borough', 'Major Category', 'Minor Category'],
                                                ID_column_name = "LSOA Code",
                                                crime_year="2019", 
                                                crime_major_category="Burglary"
                                                )

    mps_lsoa_burglary_2019_gdf = dm.convert_region_df_to_gdf(
                                                     region_gdf = london_lsoa,
                                                     df = mps_lsoa_burglary_2019,
                                                     common_column_mapper = common_column_mapper
                                                     )

    mps_ward_burglary_2019_gdf = dm.aggregate_regional_level_data(
                                                    lower_level_gdf = mps_lsoa_burglary_2019_gdf,
                                                    upper_level_gdf = london_wards,
                                                    ID_column_name = "GSS_CODE",
                                                    crs = config.CRS,
                                                    )

    # Save to disk
    mps_lsoa_burglary_2019_gdf.to_file(produces["lsoa_crime_data_cleaned"])
    mps_ward_burglary_2019_gdf.to_file(produces["ward_crime_data_cleaned"])

# %%
@pytask.mark.depends_on(
    {
        "scripts": ["clean_data.py"],
        "data_info": src / "data_management" / "data_info.yaml",
        "london_lsoa_shp": data_raw / data_info['data_raw_dirs']["statistical_gis_boundaries_london"] / data_info['data_raw_dirs']["statistical_gis_boundaries_london"] / "ESRI" / "LSOA_2011_London_gen_MHW.shp",
        "london_ward_shp": data_raw / data_info['data_raw_dirs']["statistical_gis_boundaries_london"] / data_info['data_raw_dirs']["statistical_gis_boundaries_london"] / "ESRI" / "London_Ward.shp",
        "lsoa_uk_imd_shp": data_raw / data_info['data_raw_dirs']["imd_lsoa_shp"] / "IMD_2019.shp",
    }
)
@pytask.mark.produces(
    {
        "lsoa_imd_data_cleaned": data_clean / "IMD_LSOA_2019.shp",
        "ward_imd_data_cleaned": data_clean / "IMD_Ward_2019.shp",
    }
)

def task_prepare_ward_level_IMD_data(depends_on, produces):

    # common_column_mapper = {"df": "LSOA Code",
    #                         "gdf": "LSOA11CD"}

    ## load
    london_lsoa = gpd.read_file(depends_on["london_lsoa_shp"])
    london_wards = gpd.read_file(depends_on["london_ward_shp"])
    imd_uk_lsoa = gpd.read_file(depends_on["lsoa_uk_imd_shp"])
    
    score_col_names = imd_uk_lsoa.columns[imd_uk_lsoa.columns.str.contains("Score")]
    columns_to_keep = ["lsoa11cd", "lsoa11nm", "geometry", "TotPop"] + list(score_col_names)

    # TODO: move some input parameters to data_info.yaml
    imd_london_lsoa_2019 = dm.extract_lsoa_imd_data(
                                                        imd_data = imd_uk_lsoa,
                                                        lsoa = london_lsoa,
                                                        columns_to_keep = columns_to_keep,
                                                        ID_column_name = "LSOA11CD",
                                                        
                                                    )

    imd_london_ward_2019 = dm.aggregate_regional_level_data(
                                                            lower_level_gdf = imd_london_lsoa_2019,
                                                            upper_level_gdf = london_wards,
                                                            ID_column_name = "GSS_CODE",
                                                            crs = config.CRS,
                                                            )

    # Save to disk
    imd_london_lsoa_2019.to_file(produces["lsoa_imd_data_cleaned"])
    imd_london_ward_2019.to_file(produces["ward_imd_data_cleaned"])
# %%
