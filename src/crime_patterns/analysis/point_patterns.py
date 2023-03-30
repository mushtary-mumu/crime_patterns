"""Functions for point analysis."""

import numpy as np
import xarray as xr
from scipy import stats
from sklearn.cluster import DBSCAN


def evaluate_hotspots(longitudes, latitudes, region, crs="EPSG:4326"):
    """Function to evaluate hotspots using kernel density estimation.

    Parameters
    ----------
    longitudes : array-like
        Array of longitudes.
    latitudes : array-like
        Array of latitudes.
    region : geopandas.GeoDataFrame
        GeoDataFrame containing the region of interest.
    crs : str, optional
        Coordinate reference system of the region of interest, by default "EPSG:4326"

    Returns:
    -------
    xarray.Dataset
        Dataset containing the kernel density estimates.

    """
    xmin, ymin, xmax, ymax = region.to_crs(crs).total_bounds

    X_coords, Y_coords = np.mgrid[xmin:xmax:100j, ymin:ymax:100j]

    positions = np.vstack([X_coords.ravel(), Y_coords.ravel()])
    values = np.vstack([longitudes, latitudes])

    kernel = stats.gaussian_kde(values)

    densities = np.reshape(kernel.evaluate(positions).T, X_coords.shape)

    ## Set very small densities to NaN.
    densities[np.abs(densities) <= 1] = np.nan

    da = xr.DataArray(
        data=densities,
        dims=["x", "y"],
        coords={
            "lon": (["x", "y"], X_coords),
            "lat": (["x", "y"], Y_coords),
        },
    )

    ds = da.to_dataset(name="densities")

    ds.attrs = {"Description": "Burglary Hotspots (Kernel Density Estimates)"}

    return ds


def cluster_crime_incidents_dbscan(
    latitudes,
    longitudes,
    epsilon,
    min_samples,
    **kwargs,
):
    """Function to perform DBSCAN clustering for given parameters.

    Parameters
    ----------
    latitudes : array-like
        Array of latitudes.
    longitudes : array-like
        Array of longitudes.
    epsilon : float
        Epsilon parameter for DBSCAN.
    min_samples : int
        Minimum number of samples for DBSCAN.
    **kwargs : dict
        Additional keyword arguments for DBSCAN.

    Returns:
    -------
    sklearn.cluster.DBSCAN
        DBSCAN object.

    """
    # convert epsilon from km to radians
    kms_per_radian = 6371.0088
    epsilon /= kms_per_radian

    # set up the algorithm
    dbscan = DBSCAN(
        eps=epsilon,
        min_samples=min_samples,
        algorithm="ball_tree",
        metric="haversine",
        **kwargs,
    )

    # fit the algorithm
    dbscan.fit(np.radians(list(zip(latitudes, longitudes))))

    # return the cluster labels
    return dbscan
