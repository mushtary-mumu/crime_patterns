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
import logging
logger = logging.getLogger(__name__)

src = config.SRC
bld = config.BLD
data_raw = src / "data"
data_clean = bld / "python" / "data"
downloads_dir = src / "data" / "downloads"

if not os.path.isdir(downloads_dir):
    os.makedirs(downloads_dir)

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

###### Downloading raw data ######

@pytask.mark.persist
@pytask.mark.depends_on(
    {
        "data_info": src / "data_management" / "data_info.yaml"
    }
)
@pytask.mark.produces(
    {
        "uk_crime_data_2019": downloads_dir / "uk_crime_data_2019.zip",
        "imd_lsoa": downloads_dir / "IMD_LSOA_2019.csv",
        "imd_lsoa_shp": downloads_dir / "IMD_LSOA_2019.zip",
        "statistical_gis_boundaries_london": downloads_dir / "statistical-gis-boundaries-london.zip",
        "lsoa_level_crime": downloads_dir / "MPS LSOA Level Crime (Historical).csv",
    }
)
def task_data_download(produces):

    """Clean the data (Python version)."""

    logger.warn("This task downloads large data files with approx ~ 1.7 GB filesize.")

    for url_key in data_info["urls"]:
        utils.download_file(
                            url = data_info["urls"][url_key],
                            dest_folder = downloads_dir,
                            filename = produces[url_key]
                            )

###### Unzipping downloaded data ######

@pytask.mark.depends_on(

    {
        "uk_crime_data_2019": downloads_dir / "uk_crime_data_2019.zip",
        "imd_lsoa_shp": downloads_dir / "IMD_LSOA_2019.zip",
        "statistical_gis_boundaries_london": downloads_dir / "statistical-gis-boundaries-london.zip",
    }
)
## TODO: Resolve folder-in-folder issue when unzipping folders
@pytask.mark.produces(
    {
        "uk_crime_data_2019": crime_data_filepaths,
        "imd_lsoa_shp": data_raw / data_info['data_raw_dirs']["imd_lsoa"] / "IMD_2019.shp",
        "statistical_gis_boundaries_london": [data_raw / data_info['data_raw_dirs']["statistical_gis_boundaries_london"] / data_info['data_raw_dirs']["statistical_gis_boundaries_london"] / "ESRI" / "LSOA_2011_London_gen_MHW.shp",
                                              data_raw / data_info['data_raw_dirs']["statistical_gis_boundaries_london"] / data_info['data_raw_dirs']["statistical_gis_boundaries_london"] / "ESRI" / "MSOA_2011_London_gen_MHW.shp",
                                              data_raw / data_info['data_raw_dirs']["statistical_gis_boundaries_london"] / data_info['data_raw_dirs']["statistical_gis_boundaries_london"] / "ESRI" / "London_Ward.shp"]
    }
)

def task_data_unzip(depends_on, produces):

    logger.warn("This task unzips large data files with approx ~ 2.5 GB filesize.")

    for key in depends_on:

        if key == "uk_crime_data_2019":
            # Selective extraction is performed 
            # to avoid extraction of crime data 
            # from other years (2017 and 2018)
            # that is also available in the downloaded archive.
            subset = True
            startswith = data_info["crime_year"]

        else: 
            subset = False
            startswith=None
        
        utils.unzip_folder(
            zip_file = depends_on[key],
            output_dir = data_raw,
            subset=subset, 
            startswith=startswith
            )

###### Moving and reorganizing data files in folders #######

@pytask.mark.depends_on(

    {
        "imd_lsoa": downloads_dir / "IMD_LSOA_2019.csv",
        "lsoa_level_crime": downloads_dir / "MPS LSOA Level Crime (Historical).csv",
    }
)
@pytask.mark.produces(
    {
        "imd_lsoa": data_raw / data_info['data_raw_dirs']["imd_lsoa"] / "IMD_LSOA_2019.csv",
        "lsoa_level_crime": data_raw / data_info['data_raw_dirs']["lsoa_level_crime"] / "MPS LSOA Level Crime (Historical).csv",
    }
)

def task_data_move(depends_on, produces):
    
    ## move individual files and organize into folders
    shutil.copy2(src= depends_on["imd_lsoa"],
                dst= os.path.dirname(produces["imd_lsoa"]) )

    shutil.copy2(src= depends_on["lsoa_level_crime"],
                dst= os.path.dirname(produces["lsoa_level_crime"]))

    ## clear up downloads folder
    # shutil.rmtree(downloads_dir)


# %%
