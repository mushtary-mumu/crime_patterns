"""Functions plotting results."""
import matplotlib.pyplot as plt
from cycler import cycler
import numpy as np

def plot_hotspots(X_coords, Y_coords, densities, region, crs="EPSG:4326", figsize=(8, 6)):

    fig, ax = plt.subplots(figsize=figsize)

    contours = plt.contourf(X_coords, Y_coords, densities, 7, cmap='Reds')
    cbar = plt.colorbar(contours)

    region.to_crs(crs).plot(ax=ax, fc="None")
    
    plt.axis(False)

    return fig, ax, cbar

def plot_crime_incidents(X_coords, Y_coords, region, crs="EPSG:4326", figsize=(8, 6)):

    fig, ax = plt.subplots(figsize=figsize)

    ax.scatter(X_coords, Y_coords, s=5, c='saddlebrown', linewidth=0.3, ec='sandybrown')
    region.to_crs(crs).plot(ax=ax, fc="None", alpha=1, ec="k", linewidth=1)

    plt.axis(False)

    return fig, ax


def plot_dbscan_clusters(data, labels, region, crs="EPSG:4326", figsize=(8, 6)):

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