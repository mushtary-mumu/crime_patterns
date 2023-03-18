"""Tests for the point patterns module."""
#%%
import numpy as np
import pandas as pd
import geopandas as gpd
import pytest
from crime_patterns.analysis.point_patterns import evaluate_hotspots, cluster_crime_incidents_dbscan
from shapely.geometry import box

DESIRED_PRECISION = 10e-2

# @pytest.fixture()
# def data():
#     np.random.seed(0)
#     x = np.random.normal(size=100_000)
#     coef = 2.0
#     prob = 1 / (1 + np.exp(-coef * x))
#     return pd.DataFrame(
#         {"outcome_numerical": np.random.binomial(1, prob), "covariate": x},
#     )

# @pytest.fixture()
# def data_info():
#     return {"outcome": "outcome", "outcome_numerical": "outcome_numerical"}


# def test_fit_logit_model_recover_coefficients(data, data_info):
#     model = fit_logit_model(data, data_info, model_type="linear")
#     params = model.params
#     assert np.abs(params["Intercept"]) < DESIRED_PRECISION
#     assert np.abs(params["covariate"] - 2.0) < DESIRED_PRECISION


# def test_fit_logit_model_error_model_type(data, data_info):
#     with pytest.raises(ValueError):  # noqa: PT011
#         assert fit_logit_model(data, data_info, model_type="quadratic")
#%%
@pytest.fixture()
def data():

    longitudes = np.array([0, 0, 0, 0, 0, 0, 0, 0, 0, 0])
    latitudes = np.array([0, 0, 0, 0, 0, 0, 0, 0, 0, 0])

    region = gpd.GeoDataFrame(geometry=[box(0, 0, 1, 1)], crs="EPSG:4326")

    return {"longitudes":longitudes, "latitudes":latitudes, "region":region}

#%%
@pytest.mark.skip(reason="not finalized yet")
def test_evaluate_hotspots(data):
    
    ds = evaluate_hotspots(data["longitudes"], data["latitudes"], data["region"])
    
    assert ds.densities.max() == 1.0
    assert ds.densities.min() == 1.0

#%%
@pytest.mark.skip(reason="not finalized yet")
def test_cluster_crime_incidents_dbscan(data):
    
    cluster_labels = cluster_crime_incidents_dbscan(data["longitudes"], data["latitudes"],epsilon=0.1,min_samples=1)
    
    assert cluster_labels.max() == 0
    assert cluster_labels.min() == 0

