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
    crime_data_yearly_gdf = utils.convert_points_df_to_gdf(df = crime_data_yearly).to_crs(config.CRS)
    crime_data_yearly_gdf.to_file(filename=produces["cleaned_shp"])

# %%
