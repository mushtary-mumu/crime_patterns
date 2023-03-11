"""Tasks for managing the data."""
#%%
import itertools
import os
import shutil
import numpy as np
import pandas as pd
import pytask

import crime_patterns.config as config
import crime_patterns.data_management as dm
import crime_patterns.utilities as utils 

src = config.SRC
bld = config.BLD

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
        "data_info": src / "data_management" / "data_info.yaml"
    }
)
@pytask.mark.produces(
    {
        "crime_data_filepaths": crime_data_filepaths,
        "lsoa_shp": src / "data" / "statistical-gis-boundaries-london" / "ESRI" / "LSOA_2011_London_gen_MHW.shp",
        "msoa_shp": src / "data" / "statistical-gis-boundaries-london" / "ESRI" / "MSOA_2011_London_gen_MHW.shp",
        "MPS_LSOA_crime": src / "data" / "MPS_LSOA_Level_Crime" / "MPS LSOA Level Crime (Historical).csv"
    }
)
# TODO: Use @pytask.mark.parametrize() here ?? 
# See: https://pytask-dev.readthedocs.io/en/stable/tutorials/repeating_tasks_with_different_inputs.html
def task_data_download():

    """Clean the data (Python version)."""

    downloads_dir = src / "data" / "downloads"
    unzip_dir = src / "data"
    if not os.path.isdir(downloads_dir):
        os.makedirs(downloads_dir)

    utils.download_file(
                        url = data_info["urls"]["uk_crime_data_all"],
                        dest_folder = downloads_dir,
                        filename="uk_crime_data_all.zip"
                        )

    utils.download_file(
                        url = data_info["urls"]["IMD_LSOA_shp"],
                        dest_folder = downloads_dir,
                        filename="IMD_LSOA_shp.zip"
                        )

    utils.download_file(
                        url = data_info["urls"]["IMD_LSOA"],
                        dest_folder = downloads_dir,
                        filename="IMD_LSOA.csv"
                        )
    
    utils.download_file(
                        url = data_info["urls"]["statistical_gis_boundaries_london"],
                        dest_folder = downloads_dir,
                        filename="statistical_gis_boundaries_london.zip"
                        )

    utils.download_file(
                        url = data_info["urls"]["MPS_LSOA_crime"],
                        dest_folder = downloads_dir,
                        filename="MPS LSOA Level Crime (Historical).csv"
                        )

    utils.unzip_folder(
        zipped_folder = downloads_dir / "uk_crime_data_all.zip",
        extract_to =  unzip_dir / "uk_crime_data_all"
        )
    
    utils.unzip_folder(
        zipped_folder = downloads_dir / "IMD_LSOA_shp.zip",
        extract_to =  unzip_dir / "IMD_LSOA"
        )

    utils.unzip_folder(
        zipped_folder = downloads_dir / "statistical_gis_boundaries_london.zip",
        extract_to =  unzip_dir
        )

    ## move individual files and organize into folders
    shutil.move(src= downloads_dir / "IMD_LSOA.csv",
                dst= src / "data" / "IMD_LSOA" / "IMD_LSOA.csv" )

    shutil.move(src= downloads_dir / "MPS LSOA Level Crime (Historical).csv",
                dst= src / "data" / "MPS_LSOA_Level_Crime" / "MPS LSOA Level Crime (Historical).csv" )

    ## clear up downloads folder
    shutil.rmtree(downloads_dir)

# %%
