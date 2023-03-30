"""Tests for the point patterns module."""
#%%
import numpy as np
import pytest
from crime_patterns.analysis.point_patterns import (
    cluster_crime_incidents_dbscan,
    evaluate_hotspots,
)

DESIRED_PRECISION = 10e-2

#%%
def test_evaluate_hotspots(mock_crime_points, mock_crime_polygons):
    ds = evaluate_hotspots(
        longitudes=mock_crime_points["points"].x,
        latitudes=mock_crime_points["points"].y,
        region=mock_crime_polygons,
        crs="EPSG:4326",
    )

    assert np.isclose(
        float(ds.densities.max()),
        11.90496,
        atol=pytest.DESIRED_PRECISION,
    )
    assert np.isclose(float(ds.densities.min()), 1.00051, atol=pytest.DESIRED_PRECISION)
    assert np.isclose(
        float(ds.densities.mean()),
        4.53039,
        atol=pytest.DESIRED_PRECISION,
    )


#%%
def test_cluster_crime_incidents_dbscan(mock_crime_points):
    cluster_labels = cluster_crime_incidents_dbscan(
        longitudes=mock_crime_points["points"].x,
        latitudes=mock_crime_points["points"].y,
        epsilon=6,
        min_samples=10,
    )

    assert set(cluster_labels.labels_) == {-1, 0, 1, 2}
