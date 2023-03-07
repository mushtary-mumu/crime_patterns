"""Tasks for managing the data."""
#%%
import itertools
import os

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
        "crime_data_filepaths": crime_data_filepaths
    }
)
def task_data_download():
    """Clean the data (Python version)."""

    if not os.path.isdir(src / "data" / data_info["crime_data_dir"]):
        os.makedirs(src / "data" / data_info["crime_data_dir"])

    utils.download_and_unzip(
        url = data_info["urls"]["uk_crime_data_all"],
        extract_to = src / "data" / data_info["crime_data_dir"]
        )
    
