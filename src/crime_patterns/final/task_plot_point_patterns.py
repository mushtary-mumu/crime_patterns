"""Tasks plotting the point patterns analysis results."""

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
        "scripts": ["plotting.py"],
        "crime_incidences": os.path.join(data_clean, r"city-of-london-burglaries-2019-cleaned.csv"),
        "densities": os.path.join(results_dir, "kernel_density_estimates.nc"),
        "dbscan_clusters": os.path.join(results_dir, "dbscan_clusters.pickle"),
        "london_borough": os.path.join(data_raw, "statistical-gis-boundaries-london", "statistical-gis-boundaries-london", "ESRI", "London_Borough_Excluding_MHW.shp")
    },
)
@pytask.mark.produces(
    {
    "burglary_incidents": os.path.join(plots_dir, 'burglary_incidents.png'),
    "burglary_hotspots": os.path.join(plots_dir, "burglary_hotspots.png"),
    "burglary_clusters": os.path.join(plots_dir, "burglary_clusters.png"),
    }    
)
def task_plot_point_patterns(depends_on, produces):
    
    ## Load data
    crime_incidences = pd.read_csv(depends_on["crime_incidences"])
    london_borough = gpd.read_file(depends_on["london_borough"])

    with xr.open_dataset(depends_on["densities"]) as densities:
    
        densities.load()
    X_coords, Y_coords, densities = densities["lon"].to_numpy(), densities["lat"].to_numpy(), densities["densities"].to_numpy()


    dbscan_clusters = utils.load_object_from_pickle(depends_on["dbscan_clusters"])
    labels = dbscan_clusters.labels_

    # Setup figure and axis
    height = 8
    width = height*0.75

    fig, ax = plotting.plot_crime_incidents(crime_incidences["Longitude"], crime_incidences["Latitude"], london_borough, figsize=(height, width))

    ## Plot all crime incidences
    plt.suptitle("Burglary Incidences 2019")
    fig.savefig(produces["burglary_incidents"], dpi=300, bbox_inches='tight')

    ## Plot hotspots
    fig, ax, cbar = plotting.plot_hotspots(X_coords, Y_coords, densities, london_borough, figsize=(height, width))

    cbar.ax.get_yaxis().labelpad = 15
    cbar.ax.set_ylabel("Density (KDE)", rotation=270)

    plt.suptitle("Burglary Hotspots")
    fig.savefig(produces["burglary_hotspots"], dpi=300, bbox_inches='tight')

    ## Plot clusters
    fig, ax = plotting.plot_dbscan_clusters(crime_incidences, labels, london_borough, figsize=(height, width))

    ax.legend(bbox_to_anchor = (0, 0.5))
    plt.suptitle("Clustered Burglary Incidences (DBCAN)")

    fig.savefig(produces["burglary_clusters"], dpi=300, bbox_inches='tight')
