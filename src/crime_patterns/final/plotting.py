"""Functions plotting results."""
import matplotlib.pyplot as plt
import seaborn as sns
from cycler import cycler
import numpy as np
from pysal.lib import weights
from spreg import OLS


def plot_hotspots(X_coords, Y_coords, densities, region, crs="EPSG:4326", figsize=(8, 6)):

    """Plot hotspots.
    
    Parameters:
    -----------
    X_coords: numpy.ndarray
        Array containing the X coordinates of the hotspots.
    Y_coords: numpy.ndarray
        Array containing the Y coordinates of the hotspots.
    densities: numpy.ndarray
        Array containing the densities of the hotspots.
    region: geopandas.GeoDataFrame
        GeoDataFrame containing the region to be plotted.
    crs: str
        Coordinate reference system of the region.
    figsize: tuple
        Size of the figure.

    Returns:
    --------    
    fig: matplotlib.figure.Figure
        Figure containing the plot.
    ax: matplotlib.axes._subplots.AxesSubplot
        Axes containing the plot.
    cbar: matplotlib.colorbar.Colorbar
        Colorbar of the plot.

    """

    fig, ax = plt.subplots(figsize=figsize)

    contours = plt.contourf(X_coords, Y_coords, densities, 7, cmap='Reds')
    cbar = plt.colorbar(contours)

    region.to_crs(crs).plot(ax=ax, fc="None")
    
    plt.axis(False)

    return fig, ax, cbar

def plot_crime_incidents(X_coords, Y_coords, region, crs="EPSG:4326", figsize=(8, 6)):

    """Plot crime incidents.
    
    Parameters:
    -----------
    X_coords: numpy.ndarray
        Array containing the X coordinates of the crime incidents.
    Y_coords: numpy.ndarray 
        Array containing the Y coordinates of the crime incidents.
    region: geopandas.GeoDataFrame  
        GeoDataFrame containing the region to be plotted.
    crs: str
        Coordinate reference system of the region.
    figsize: tuple
        Size of the figure.

    Returns:   
    --------
    fig: matplotlib.figure.Figure
        Figure containing the plot.
    ax: matplotlib.axes._subplots.AxesSubplot
        Axes containing the plot.
            
    """

    fig, ax = plt.subplots(figsize=figsize)

    ax.scatter(X_coords, Y_coords, s=5, c='saddlebrown', linewidth=0.3, ec='sandybrown')
    region.to_crs(crs).plot(ax=ax, fc="None", alpha=1, ec="k", linewidth=1)

    plt.axis(False)

    return fig, ax


def plot_dbscan_clusters(data, labels, region, crs="EPSG:4326", figsize=(8, 6)):

    """Plot DBSCAN clusters.
    
    Parameters:
    -----------
    data: pandas.DataFrame
        DataFrame containing the data to be plotted.
    labels: numpy.ndarray   
        Array containing the cluster labels.
    region: geopandas.GeoDataFrame
        GeoDataFrame containing the region to be plotted.
    crs: str    
        Coordinate reference system of the region.
    figsize: tuple
        Size of the figure.
    
    Returns:    
    --------
    fig: matplotlib.figure.Figure
        Figure containing the plot.
    ax: matplotlib.axes._subplots.AxesSubplot
        Axes containing the plot.       
    
    """

    fig, ax = plt.subplots(figsize=figsize)

    ax.set_prop_cycle(cycler('color', ['c', 'm', 'y', 'k']))

    for lbl in sorted(np.unique(labels)):

        if lbl != -1:
            ax.scatter(data.loc[labels == lbl, "Longitude"], data.loc[labels == lbl, "Latitude"], s=9, linewidth=0.5, ec='gray', zorder=0, label=f"Cluster {lbl}")

        else:
            ## noise
            ax.scatter(data.loc[labels == lbl, "Longitude"], data.loc[labels == lbl, "Latitude"], c="lightgray", s=9, linewidth=0.5, ec='gray', zorder=0, label="Noise")

    ax.legend()

    region.to_crs(crs).plot(ax=ax, fc="None", alpha=1, ec="k", linewidth=1)

    plt.axis(False)

    return fig, ax

def plot_choropleth_map(region, column_name, figsize=(8, 6), choropleth_kwds=None, **kwargs):

    """Plot regional level data on to a choropleth map.
    
    Parameters:
    -----------
    region: geopandas.GeoDataFrame
        GeoDataFrame containing the region of interest.

    column_name: str
        Name of the column to plot.

    choropleth_kwds: dict
        Keywords used for creating and designing the choropleth map.
    
    kwargs: dict
        Dictionary containing the additional keyword arguments to be passed to the geogpandas.GeoDataFrame.plot function.

    figsize: tuple
        Size of the figure.

    Returns:
    --------
    fig, ax: matplotlib.pyplot.figure, matplotlib.pyplot.axes
        Figure and axes of the plot.

    """

    fig, ax = plt.subplots(figsize=figsize)

    if choropleth_kwds is None:
        choropleth_kwds = {}

    choropleth_kwds.setdefault("cmap", "Reds")
    choropleth_kwds.setdefault("legend", True)
    choropleth_kwds.setdefault("scheme", "Quantiles")
    choropleth_kwds.setdefault("k", 5)
    choropleth_kwds.setdefault("edgecolor", "white")
    choropleth_kwds.setdefault("linewidth", 0.0)
    choropleth_kwds.setdefault("alpha", 0.75)
    choropleth_kwds.setdefault("legend_kwds", {"loc": 2})

    region.plot(ax=ax, column=column_name, **choropleth_kwds, **kwargs)

    return fig, ax

def plot_weights_matrix(region, weights_matrix, figsize=(8, 6)):

    """Plot weights matrix.

    Parameters:
    -----------
    region: geopandas.GeoDataFrame
        GeoDataFrame containing the region to be plotted.
    weights_matrix: libpysal.weights.weights.W
        Weights matrix to be plotted.
    figsize: tuple
        Size of the figure.

    Returns:
    --------
    fig, ax: matplotlib.pyplot.figure, matplotlib.pyplot.axes
        Figure and axes of the plot.
    
    """

    fig, ax = plt.subplots(figsize=figsize)

    region.plot(ax=ax, edgecolor='grey', facecolor='w')

    weights_matrix.plot(region, 
                        ax=ax,
                        edge_kws=dict(color='darkorange', linestyle=':', linewidth=1.3),
                        node_kws=dict(marker='')
                    )

    ax.set_axis_off()

    return fig, ax

def plot_moran_scatter(moran, figsize=(8, 6)):


    """Plot Moran scatter plot.
    
    Parameters:
    -----------
    moran: esda.moran.Moran
        Moran object containing the data to be plotted.
    figsize: tuple
        Size of the figure.

    Returns:
    --------
    fig, ax: matplotlib.pyplot.figure, matplotlib.pyplot.axes
        Figure and axes of the plot.
         
    """

    fig, ax = plt.subplots(figsize=figsize)

    colors = dict(points="#bababa", fit="#d6604d")

    # set labels

    ax.set_title("Moran Scatterplot" + " (" + str(round(moran.I, 2)) + ")")
    
    lag = weights.lag_spatial(moran.w, moran.z)
    fit = OLS(moran.z[:, None], lag[:, None])
    # plot
    ax.scatter(moran.z, lag, alpha=0.6, color=colors["points"], s=40)
    ax.plot(lag, fit.predy, color=colors["fit"], alpha=0.9)
    # v- and hlines
    ax.axvline(0, alpha=0.5, color="k", linestyle="--")
    ax.axhline(0, alpha=0.5, color="k", linestyle="--")

    return fig, ax


def plot_moran_distribution(moran, figsize=(8, 6)):

    """Plot Moran distribution.
    
    Parameters:
    -----------
    moran: esda.moran.Moran
        Moran object containing the data to be plotted.
    figsize: tuple
        Size of the figure.
    Returns:
    --------    
    fig, ax: matplotlib.pyplot.figure, matplotlib.pyplot.axes
        Figure and axes of the plot.
          
        
    """
    fig, ax = plt.subplots(figsize=figsize)

    colors = dict(points="#bababa", fit="#d6604d")

    # plot distribution
    sns.kdeplot(moran.sim, fill=True, color=colors["points"], ax=ax)

    # customize plot
    ax.vlines(moran.I, 0, 1, colors["fit"])
    ax.vlines(moran.EI, 0, 1)
    ax.set_title("Reference Distribution")
    ax.set_xlabel(f"Moran I: {str(round(moran.I, 2))}")

    return fig, ax