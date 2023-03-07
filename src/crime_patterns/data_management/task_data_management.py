"""Tasks for managing the data."""
#%%
import pandas as pd
import numpy as np
import itertools
import os
import pytask

from crime_patterns.config import BLD, SRC
from crime_patterns.data_management import clean_data
from crime_patterns.utilities import read_yaml

years = ["%.2d" % i for i in np.arange(2020, 2023, 1)]
months = ["%.2d" % i for i in np.arange(1, 13, 1)]
data_info = read_yaml(SRC / "data_management" / "data_info.yaml")
crime_data_filepaths = {f"{year}-{month}": os.path.join(SRC / "data" / data_info["crime_data_dir"], f"{year}-{month}", f"{year}-{month}-city-of-london-street.csv") 
                        for year, month in itertools.product(years, months)}

# removing keys corresponding to missing data for year/month
crime_data_filepaths.pop('2020-01', None)
crime_data_filepaths.pop('2022-06', None)            

#%%
@pytask.mark.depends_on(
    {
        "scripts": ["clean_data.py"],
        "data_info": SRC / "data_management" / "data_info.yaml",
        "crime_data_filepaths": crime_data_filepaths
    },
)

@pytask.mark.produces(BLD / "python" / "data" / "city-of-london-crimes-2020-2022-cleaned.csv")
def task_clean_data_python(depends_on, produces):

    """Clean the data (Python version)."""
    # data_info = read_yaml(SRC / "data_management" / "data_info.yaml")

    # years = ["%.2d" % i for i in np.arange(2020, 2023, 1)]
    # months = ["%.2d" % i for i in np.arange(1, 13, 1)]
    crime_data_monthly = [clean_data.load_and_clean_monthly_crime_data(
                                                                       crime_incidence_filepath=depends_on["crime_data_filepaths"][key],
                                                                       year=key.split("-")[0],
                                                                       month=key.split("-")[1],
                                                                       data_info = data_info,
                                                                       ) for key in depends_on["crime_data_filepaths"].keys()]
    crime_data_yearly = pd.concat(crime_data_monthly)
    crime_data_yearly.to_csv(produces, index=False)

    # cleaned_data_dir = r"C:\Users\Mumu\Desktop\Bonn E con\Winter22-23\EPP\crime_patterns\bld\python\data"
    # crime_data_yearly.to_csv(os.path.join(cleaned_data_dir, f"city-of-london-crimes-{years[0]}-{years[-1]}-cleaned.csv"))

# %%
