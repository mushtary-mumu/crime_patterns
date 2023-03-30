"""Tasks running the core analyses."""
#%%
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
from crime_patterns.analysis import spatial_regression

## define paths
src = config.SRC
bld = config.BLD
data_raw = src / "data"
data_clean = bld / "python" / "data"
models_dir = bld / "python" / "models"
results_dir = bld / "python" / "results" 
plots_dir = bld / "python" / "figures"
shapefiles_dir = data_raw / "statistical-gis-boundaries-london" / "statistical-gis-boundaries-london", "ESRI"

if not os.path.isdir(results_dir):
    os.makedirs(results_dir)

if not os.path.isdir(plots_dir):
    os.makedirs(plots_dir)
#%%
@pytask.mark.depends_on(
    {
        "scripts": ["point_patterns.py"],
        "crime_incidences": os.path.join(data_clean, r"city-of-london-burglaries-2019-cleaned.csv"),
        "london_greater_area": os.path.join(data_clean,  "Greater_London_Area.shp")
    }
)
@pytask.mark.produces(
    {
    "densities": os.path.join(results_dir, "kernel_density_estimates.nc"),
    "dbscan_clusters": os.path.join(models_dir, "dbscan_clusters.pickle")
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

#%%

@pytask.mark.depends_on(
    {
        "scripts": ["spatial_regression.py"],
        "burglary_ward_shp_path": os.path.join(data_clean, r"MPS_Ward_Level_burglary_2019.shp"),
    },
)
@pytask.mark.produces(
    {
    "weights_matrix_ward": os.path.join(models_dir, "weights_matrix_ward.pickle"),
    "moran": os.path.join(models_dir, "moran.pickle"),
    "burglary_ward_lag": os.path.join(results_dir, "burglary_ward_lag.shp"),
    }
)
def task_spatial_autocorrelation_analysis(depends_on, produces):
    
    ## Load data
    burglary_ward = gpd.read_file(depends_on["burglary_ward_shp_path"])

    ## Calculate weights matrix
    w_knn_8_ward = spatial_regression.create_weights_matrix(burglary_ward, method="knn", k=8)

    ## Calculate spatial lag
    burglary_ward_lag = spatial_regression.calculate_spatial_lag(data=burglary_ward, y_col_name="2019_total", weights_matrix=w_knn_8_ward, ID_column_name="GSS_CODE")

    ## Calculate Moran's I
    moran = spatial_regression.calculate_morans_I(data=burglary_ward, y_col_name="2019_total", weights_matrix=w_knn_8_ward, transform="R")
    
    ## Save weights matrix and Moran
    utils.save_object_to_pickle(w_knn_8_ward, produces["weights_matrix_ward"])
    utils.save_object_to_pickle(moran, produces["moran"])

    ## Save spatial lags
    burglary_ward_lag.to_file(produces["burglary_ward_lag"])

@pytask.mark.depends_on(
    {
        "scripts": ["spatial_regression.py"],
        "imd_ward_shp_path": os.path.join(data_clean, r"IMD_Ward_2019.shp"),
        "burglary_ward_shp_path": os.path.join(data_clean, r"MPS_Ward_Level_burglary_2019.shp"),
        "pop_ward_shp_path": os.path.join(data_clean, r"Population_Ward_2019.shp"),
    },
)
@pytask.mark.produces(
    {
    "model_spatial_ols": os.path.join(models_dir, "model_spatial_ols.pickle"),
    "model_spatial_ml_lag": os.path.join(models_dir, "model_spatial_ml_lag.pickle"),
    "model_spatial_ml_error": os.path.join(models_dir, "model_spatial_ml_error.pickle"),
    "summary_spatial_ols_csv": os.path.join(results_dir, "model_spatial_ols_summary.csv"),
    "summary_spatial_ml_lag_csv": os.path.join(results_dir, "model_spatial_ml_lag_summary.csv"),
    "summary_spatial_ml_error_csv": os.path.join(results_dir, "model_spatial_ml_error_summary.csv"),
    }
)
def task_spatial_regression_analysis(depends_on, produces):
    
    ## Load data
    imd_ward = gpd.read_file(depends_on["imd_ward_shp_path"])
    burglary_ward = gpd.read_file(depends_on["burglary_ward_shp_path"])
    pop_ward = gpd.read_file(depends_on["pop_ward_shp_path"])

    ## Merge data
    db = spatial_regression.prepare_data_for_spatial_regression(crime_data=burglary_ward, explanatory_data=imd_ward, population=pop_ward, crime_col_name="2019_total", population_col_name="TotPop", ID_col_name="GSS_CODE", standardize=True)
    db = db.rename(columns={"2019_total_rate": "burglaryRate2019"})

    dependent_variable_name = 'burglaryRate2019'
    independent_variable_names = ['IncScore', 'EmpScore', 'EnvScore', 'BHSScore', 'EduScore']

    ## Run spatial regression
    model_ols = spatial_regression.perform_spatial_regression(db, dependent_variable_name, independent_variable_names, method="OLS")
    model_ml_lag = spatial_regression.perform_spatial_regression(db, dependent_variable_name, independent_variable_names, method="ML_Lag")
    model_ml_error = spatial_regression.perform_spatial_regression(db, dependent_variable_name, independent_variable_names, method="ML_Error")

    ## Save models
    utils.save_object_to_pickle(model_ols, produces["model_spatial_ols"])
    utils.save_object_to_pickle(model_ml_lag, produces["model_spatial_ml_lag"])
    utils.save_object_to_pickle(model_ml_error, produces["model_spatial_ml_error"])

    ## Save summaries
    spatial_regression.get_reg_summary(model_ols, "OLS").to_csv(produces["summary_spatial_ols_csv"])
    spatial_regression.get_reg_summary(model_ml_lag, "ML_Lag").to_csv(produces["summary_spatial_ml_lag_csv"])
    spatial_regression.get_reg_summary(model_ml_error, "ML_Error").to_csv(produces["summary_spatial_ml_error_csv"])
