"""Functions for point analysis."""

import numpy as np
from scipy import stats
from sklearn.cluster import DBSCAN

def evaluate_hotspots(longitudes, latitudes, region, crs="EPSG:4326"):

    xmin, ymin, xmax, ymax = region.to_crs(crs).total_bounds

    X_coords, Y_coords = np.mgrid[xmin:xmax:100j, ymin:ymax:100j]

    positions = np.vstack([X_coords.ravel(), Y_coords.ravel()])
    values = np.vstack([longitudes, latitudes])
    
    kernel = stats.gaussian_kde(values)

    densities = np.reshape(kernel.evaluate(positions).T, X_coords.shape)
    
    ## Set very small densities to NaN.
    densities[np.abs(densities) <= 1] = np.nan

    return X_coords, Y_coords, densities

