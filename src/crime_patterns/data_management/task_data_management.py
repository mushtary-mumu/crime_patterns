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

## TODO: consider moving some of the things to config.py or data_info.yml
years = ["%.2d" % i for i in np.arange(2020, 2023, 1)]
months = ["%.2d" % i for i in np.arange(1, 13, 1)]
data_info = utils.read_yaml(src / "data_management" / "data_info.yaml")
crime_data_filepaths = {
    f"{year}-{month}": os.path.join(
        src / "data" / data_info["crime_data_dir"],
        f"{year}-{month}",
        f"{year}-{month}-city-of-london-street.csv",
    )
    for year, month in itertools.product(years, months)
}

# removing keys corresponding to missing data for year/month
crime_data_filepaths.pop("2020-01", None)
crime_data_filepaths.pop("2022-06", None)

#%%
@pytask.mark.depends_on(
    {
        "scripts": ["clean_data.py"],
        "data_info": src / "data_management" / "data_info.yaml",
        "crime_data_filepaths": crime_data_filepaths,
    },
)
@pytask.mark.produces(
    {
        "cleaned_csv": bld / "python" / "data" / "city-of-london-crimes-2020-2022-cleaned.csv",
        "cleaned_shp": bld / "python" / "data" / "city-of-london-crimes-2020-2022-cleaned.shp",
    }
)
def task_clean_data_python(depends_on, produces):
    """Clean the data (Python version)."""
    crime_data_monthly = [
        dm.clean_monthly_crime_data(
            crime_incidence_filepath=depends_on["crime_data_filepaths"][key],
            year=key.split("-")[0],
            month=key.split("-")[1],
            data_info=data_info,
        )
        for key in depends_on["crime_data_filepaths"]
    ]
    crime_data_yearly = pd.concat(crime_data_monthly)
    crime_data_yearly.to_csv(produces["cleaned_csv"], index=False)

    ## TODO: consider renaming columns that have more than 10 characters to avoid truncation
    crime_data_yearly_gdf = dm.convert_points_df_to_gdf(df = crime_data_yearly).to_crs(config.CRS)
    crime_data_yearly_gdf.to_file(filename=produces["cleaned_shp"])

# %%
@pytask.mark.depends_on(
    {
        "scripts": ["clean_data.py"],
        "data_info": src / "data_management" / "data_info.yaml",
        "london_lsoa_shp": src / "data" / "statistical-gis-boundaries-london" / "ESRI" / "LSOA_2011_London_gen_MHW.shp",
        "london_ward_shp": src / "data" / "statistical-gis-boundaries-london" / "ESRI" / "London_Ward.shp",
        "lsoa_crime_data": src / "data" / "MPS_LSOA_Level_Crime" / "MPS LSOA Level Crime (Historical).csv"
    },
)
@pytask.mark.produces(
    {
        "lsoa_crime_data_cleaned": bld / "python" / "data" / "MPS_LSOA_Level_burglary_2019.shp",
        "ward_crime_data_cleaned": bld / "python" / "data" / "MPS_Ward_Level_burglary_2019.shp",
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
                                                    )

    # Save to disk
    mps_lsoa_burglary_2019_gdf.to_file(produces["lsoa_crime_data_cleaned"])
    mps_ward_burglary_2019_gdf.to_file(produces["ward_crime_data_cleaned"])

# %%
