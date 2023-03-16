"""Tasks running the core analyses."""

import numpy as np
import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
from os.path import join
import os
import pytask
import xarray as xr

import crime_patterns.utilities as utils
import crime_patterns.config as config
import crime_patterns.data_management as dm

from crime_patterns.final import plotting
from crime_patterns.analysis import point_patterns 

## define paths
src = config.SRC
bld = config.BLD
data_raw = src / "data"
data_clean = bld / "python" / "data"
results_dir = bld / "python" / "results" 
plots_dir = bld / "python" / "figures"

if not os.path.isdir(results_dir):
    os.makedirs(results_dir)

if not os.path.isdir(plots_dir):
    os.makedirs(plots_dir)

@pytask.mark.depends_on(
    {
        "scripts": ["point_patterns.py"],
        "crime_incidences": os.path.join(data_clean, r"city-of-london-burglaries-2019-cleaned.csv"),
        "london_greater_area": os.path.join(data_clean,  "Greater_London_Area.shp")
    },
)
@pytask.mark.produces(
    {
    "densities": os.path.join(results_dir, "kernel_density_estimates.nc"),
    "dbscan_clusters": os.path.join(results_dir, "dbscan_clusters.pickle")
    }    
)
def task_point_patterns_analysis(depends_on, produces):
    
    ## Load data
    london_greater_area = gpd.read_file(depends_on["london_greater_area"])
    crime_incidences = pd.read_csv(depends_on["crime_incidences"])
    densities = point_patterns.evaluate_hotspots(longitudes=crime_incidences["Longitude"], 
                                                 latitudes=crime_incidences["Latitude"], 
                                                 region=london_greater_area)
    
    dbscan_clusters = point_patterns.cluster_crime_incidents_dbscan(
                                                latitudes=crime_incidences["Latitude"],
                                                longitudes=crime_incidences["Longitude"],
                                                epsilon=1.5, # km
                                                min_samples=330,
                                                )

    densities.to_netcdf(produces["densities"], mode='w', format="NETCDF4", engine="netcdf4")
    utils.save_object_to_pickle(dbscan_clusters, produces["dbscan_clusters"])

