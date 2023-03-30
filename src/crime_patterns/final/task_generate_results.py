"""Tasks plotting the point patterns analysis results."""
#%%

import os

import geopandas as gpd
import matplotlib.pyplot as plt
import pandas as pd
import pytask
import xarray as xr

import crime_patterns.config as config
import crime_patterns.utilities as utils
from crime_patterns.analysis import spatial_regression
from crime_patterns.final import plotting

## define paths
src = config.SRC
bld = config.BLD
data_raw = src / "data"
data_clean = bld / "python" / "data"
results_dir = bld / "python" / "results"
models_dir = bld / "python" / "models"
plots_dir = bld / "python" / "figures"
tables_dir = bld / "python" / "tables"

if not os.path.isdir(results_dir):
    os.makedirs(results_dir)

if not os.path.isdir(plots_dir):
    os.makedirs(plots_dir)

#%%
@pytask.mark.depends_on(
    {
        "scripts": ["plotting.py"],
        "crime_incidences": os.path.join(
            data_clean,
            r"city-of-london-burglaries-2019-cleaned.csv",
        ),
        "densities": os.path.join(results_dir, "kernel_density_estimates.nc"),
        "dbscan_clusters": os.path.join(results_dir, "dbscan_clusters.pickle"),
        "london_borough": os.path.join(
            data_raw,
            "statistical-gis-boundaries-london",
            "statistical-gis-boundaries-london",
            "ESRI",
            "London_Borough_Excluding_MHW.shp",
        ),
    },
)
@pytask.mark.produces(
    {
        "burglary_incidents": os.path.join(plots_dir, "burglary_incidents.png"),
        "burglary_hotspots": os.path.join(plots_dir, "burglary_hotspots.png"),
        "burglary_clusters": os.path.join(plots_dir, "burglary_clusters.png"),
    },
)
def task_plot_point_patterns(depends_on, produces):
    ## Load data
    crime_incidences = pd.read_csv(depends_on["crime_incidences"])
    london_borough = gpd.read_file(depends_on["london_borough"])

    with xr.open_dataset(depends_on["densities"]) as densities:

        densities.load()
    X_coords, Y_coords, densities = (
        densities["lon"].to_numpy(),
        densities["lat"].to_numpy(),
        densities["densities"].to_numpy(),
    )

    dbscan_clusters = utils.load_object_from_pickle(depends_on["dbscan_clusters"])
    labels = dbscan_clusters.labels_

    # Setup figure and axis
    height = 8
    width = height * 0.75

    fig, ax = plotting.plot_crime_incidents(
        crime_incidences["Longitude"],
        crime_incidences["Latitude"],
        london_borough,
        figsize=(height, width),
    )

    ## Plot all crime incidences
    plt.suptitle("Burglary Incidences 2019")
    fig.savefig(produces["burglary_incidents"], dpi=300, bbox_inches="tight")

    ## Plot hotspots
    fig, ax, cbar = plotting.plot_hotspots(
        X_coords,
        Y_coords,
        densities,
        london_borough,
        figsize=(height, width),
    )

    cbar.ax.get_yaxis().labelpad = 15
    cbar.ax.set_ylabel("Density (KDE)", rotation=270)

    plt.suptitle("Burglary Hotspots")
    fig.savefig(produces["burglary_hotspots"], dpi=300, bbox_inches="tight")

    ## Plot clusters
    fig, ax = plotting.plot_dbscan_clusters(
        crime_incidences,
        labels,
        london_borough,
        figsize=(height, width),
    )

    ax.legend(bbox_to_anchor=(0, 0.5))
    plt.suptitle("Clustered Burglary Incidences (DBCAN)")

    fig.savefig(produces["burglary_clusters"], dpi=300, bbox_inches="tight")


@pytask.mark.depends_on(
    {
        "scripts": ["plotting.py"],
        "london_borough": os.path.join(
            data_raw,
            "statistical-gis-boundaries-london",
            "statistical-gis-boundaries-london",
            "ESRI",
            "London_Borough_Excluding_MHW.shp",
        ),
        "imd_ward": os.path.join(data_clean, r"IMD_Ward_2019.shp"),
        "imd_lsoa": os.path.join(data_clean, r"IMD_LSOA_2019.shp"),
        "burglary_ward": os.path.join(data_clean, r"MPS_Ward_Level_burglary_2019.shp"),
    },
)
@pytask.mark.produces(
    {
        "imd_scores_lsoa": os.path.join(plots_dir, "imd_scores_lsoa.png"),
        "imd_scores_ward": os.path.join(plots_dir, "imd_scores_ward.png"),
        "burglary_ward": os.path.join(plots_dir, "burglary_ward.png"),
    },
)
def task_plot_cleaned_data(depends_on, produces):
    ## Load Data
    london_borough = gpd.read_file(depends_on["london_borough"])

    imd_ward = gpd.read_file(depends_on["imd_ward"])
    imd_lsoa = gpd.read_file(depends_on["imd_lsoa"])
    burglary_ward = gpd.read_file(depends_on["burglary_ward"])

    # Setup figure and axis
    height = 8
    width = height * 0.75

    ### Plot LSOA level IMD scores
    choropleth_kwds = {"scheme": "natural_breaks", "cmap": "viridis_r"}

    fig, ax = plotting.plot_choropleth_map(
        region=imd_lsoa,
        column_name="IMDScore",
        figsize=(height, width),
        choropleth_kwds=choropleth_kwds,
    )

    london_borough.to_crs(imd_lsoa.crs).plot(ax=ax, fc="None")

    ax.set_axis_off()
    ax.set_title("IMD Score by LSOA")
    fig.savefig(produces["imd_scores_lsoa"], dpi=300, bbox_inches="tight")

    ### Plot Ward level IMD scores
    fig, ax = plotting.plot_choropleth_map(
        region=imd_ward,
        column_name="IMDScore",
        figsize=(height, width),
        choropleth_kwds=choropleth_kwds,
    )

    london_borough.to_crs(imd_ward.crs).plot(ax=ax, fc="None")

    ax.set_axis_off()
    ax.set_title("IMD Score by Ward")
    fig.savefig(produces["imd_scores_ward"], dpi=300, bbox_inches="tight")

    ### Plot Ward level burglary counts
    choropleth_kwds = {"scheme": "natural_breaks", "cmap": "Reds"}

    fig, ax = plotting.plot_choropleth_map(
        region=burglary_ward,
        column_name="2019_total",
        figsize=(height, width),
        choropleth_kwds=choropleth_kwds,
    )

    london_borough.to_crs(burglary_ward.crs).plot(ax=ax, fc="None")

    ax.set_axis_off()
    ax.set_title("No. of Burglaries by Ward")
    fig.savefig(produces["burglary_ward"], dpi=300, bbox_inches="tight")


# %%
@pytask.mark.depends_on(
    {
        "scripts": ["plotting.py"],
        "moran": os.path.join(models_dir, "moran.pickle"),
        "weights_matrix_ward": os.path.join(models_dir, "weights_matrix_ward.pickle"),
        "london_ward": os.path.join(
            data_raw,
            "statistical-gis-boundaries-london",
            "statistical-gis-boundaries-london",
            "ESRI",
            "London_Ward.shp",
        ),
        "london_borough": os.path.join(
            data_raw,
            "statistical-gis-boundaries-london",
            "statistical-gis-boundaries-london",
            "ESRI",
            "London_Borough_Excluding_MHW.shp",
        ),
        "burglary_ward_lag": os.path.join(results_dir, "burglary_ward_lag.shp"),
    },
)
@pytask.mark.produces(
    {
        "moran_scatter": os.path.join(plots_dir, "moran_scatter.png"),
        "moran_distribution": os.path.join(plots_dir, "moran_distribution.png"),
        "burglary_ward_lag": os.path.join(plots_dir, "burglary_ward_lag.png"),
        "weights_matrix_ward": os.path.join(plots_dir, "weights_matrix_ward.png"),
    },
)
def task_plot_spatial_autocorrelation(depends_on, produces):
    ## Load Data
    moran = utils.load_object_from_pickle(depends_on["moran"])
    burglary_ward_lag = gpd.read_file(depends_on["burglary_ward_lag"])
    london_borough = gpd.read_file(depends_on["london_borough"])
    london_ward = gpd.read_file(depends_on["london_ward"])

    # Setup figure and axis
    height = 8
    width = height * 0.75

    ## Plot Moran's I Scatter
    fig, ax = plotting.plot_moran_scatter(moran)

    ax.set_xlabel("Burglary, 2019")
    ax.set_ylabel("Burglary - Spatial Lag, 2019")
    fig.savefig(produces["moran_scatter"], dpi=300, bbox_inches="tight")

    ## Plot Moran's I Distribution
    fig, ax = plotting.plot_moran_distribution(moran)
    fig.savefig(produces["moran_distribution"], dpi=300, bbox_inches="tight")

    ## Plot Burglary Spatial Lag
    fig, ax = plotting.plot_choropleth_map(
        region=burglary_ward_lag,
        column_name="lag",
        figsize=(height, width),
    )

    london_borough.to_crs(burglary_ward_lag.crs).plot(ax=ax, fc="None")

    ax.set_title("Burglary 2019 - Spatial Lag")
    ax.set_axis_off()
    fig.savefig(produces["burglary_ward_lag"], dpi=300, bbox_inches="tight")

    ## Plot Spatial Weights Matrix
    w_knn_8_ward = utils.load_object_from_pickle(depends_on["weights_matrix_ward"])
    fig, ax = plotting.plot_weights_matrix(london_ward, w_knn_8_ward, figsize=(8, 6))
    fig.savefig(produces["weights_matrix_ward"], dpi=300, bbox_inches="tight")


# %%
@pytask.mark.depends_on(
    {
        "model_spatial_ols": os.path.join(models_dir, "model_spatial_ols.pickle"),
        "model_spatial_ml_lag": os.path.join(models_dir, "model_spatial_ml_lag.pickle"),
        "model_spatial_ml_error": os.path.join(
            models_dir,
            "model_spatial_ml_error.pickle",
        ),
    },
)
@pytask.mark.produces(
    {
        "summary_spatial_ols_tex": os.path.join(
            tables_dir,
            "model_spatial_ols_summary.tex",
        ),
        "summary_spatial_ml_lag_tex": os.path.join(
            tables_dir,
            "model_spatial_ml_lag_summary.tex",
        ),
        "summary_spatial_ml_error_tex": os.path.join(
            tables_dir,
            "model_spatial_ml_error_summary.tex",
        ),
    },
)
def task_create_latex_tables(depends_on, produces):
    ## Load models
    model_ols = utils.load_object_from_pickle(depends_on["model_spatial_ols"])
    model_ml_lag = utils.load_object_from_pickle(depends_on["model_spatial_ml_lag"])
    model_ml_error = utils.load_object_from_pickle(depends_on["model_spatial_ml_error"])

    ## Save summaries
    spatial_regression.get_reg_summary(model_ols, "OLS").to_latex(
        produces["summary_spatial_ols_tex"],
    )
    spatial_regression.get_reg_summary(model_ml_lag, "ML_Lag").to_latex(
        produces["summary_spatial_ml_lag_tex"],
    )
    spatial_regression.get_reg_summary(model_ml_error, "ML_Error").to_latex(
        produces["summary_spatial_ml_error_tex"],
    )
