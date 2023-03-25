"""Functions for point analysis."""

import numpy as np
import xarray as xr
from scipy import stats
from sklearn.cluster import DBSCAN

from libpysal.weights import Queen, Rook, KNN
from pysal.explore import esda

def create_weights_matrix(data, method="queen", k=5, **kwargs):

    """Create weights matrix.
    
    Parameters:
    -----------
    data: geopandas.GeoDataFrame
        GeoDataFrame containing the data to be used for creating the weights matrix.
    method: str
        Method to be used for creating the weights matrix. Options are:
        - "queen"
        - "rook"
        - "knn"
    k: int
        Number of nearest neighbors to be used for creating the weights matrix.
    **kwargs: dict
        Keyword arguments to be passed to the weights matrix creation function.
    
    Returns:
    --------
    w: libpysal.weights.weights.W
        Weights matrix.
    
    """
    
    if method == "queen":
        w = Queen.from_dataframe(data, **kwargs)
        
    elif method == "rook":
        w = Rook.from_dataframe(data, **kwargs)
        
    elif method == "knn":
        w = KNN.from_dataframe(data, k=k, **kwargs)
        
    else:
        raise ValueError("Invalid method. Valid options are: 'queen', 'rook', 'knn'.")
        
    return w

def calculate_spatial_lag(data, y_col_name, weights_matrix, ID_column_name, transform="R"):

    """Calculate spatial lag.
        
        Parameters:
        -----------
        data: geopandas.GeoDataFrame
            GeoDataFrame containing the data to be used for calculating the spatial lag.
        y_col_name: str
            Name of the column containing the variable to be used for calculating the spatial lag.
        weights_matrix: libpysal.weights.weights.W
            Weights matrix to be used for calculating the spatial lag.
        ID_column_name: str
            Name of the column containing the ID of the observations.
        transform: str
            Transform to be applied to the weights matrix. Options are:
            -   R ; Row-standardization (global sum)
            -   D ; Double-standardization (global sum)
            -   V ; Variance stabilizing
            -   O ; Restore original transformation (from instantiation)
        
        Returns:
        --------
        spatial_lag: geopandas.GeoDataFrame
            GeoDataFrame containing the spatial lag.
        
        """
        
    data = data.set_index(ID_column_name)

    weights_matrix.transform = transform

    data[f"{y_col_name}_lag"] = weights_matrix.sparse * data[y_col_name].values

    spatial_lag = data[[y_col_name, f"{y_col_name}_lag", "geometry"]]

    return spatial_lag

def calculate_morans_I(data, y_col_name, weights_matrix, permutations=999, transform="R"):

    """Calculate Moran's I.
    
    Parameters:
    -----------
    data: geopandas.GeoDataFrame
        GeoDataFrame containing the data to be used for calculating Moran's I.
    y_col_name: str
        Name of the column containing the variable to be used for calculating Moran's I.
    weights_matrix: libpysal.weights.distance.KNN
        Weights matrix to be used for calculating Moran's I.
    ID_column_name: str
        Name of the column containing the ID of the observations.
    transform: str
        Transform to be applied to the weights matrix. Options are:
        -   R ; Row-standardization (global sum)
        -   D ; Double-standardization (global sum)
        -   V ; Variance stabilizing
        -   O ; Restore original transformation (from instantiation)
    
    Returns:
    --------
    moran: esda.moran.Moran
    
    """

    weights_matrix.transform = transform

    moran = esda.moran.Moran(data[y_col_name], weights_matrix, permutations=permutations)

    return moran