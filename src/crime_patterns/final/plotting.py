"""Functions plotting results."""
import matplotlib.pyplot as plt

def plot_hotspots(X_coords, Y_coords, densities, region, crs="EPSG:4326"):

    fig, ax = plt.subplots(figsize=(8, 6))

    plt.contourf(X_coords, Y_coords, densities, 7, cmap='Reds')
    plt.colorbar()

    region.to_crs(crs).plot(ax=ax, fc="None")

    plt.axis(False)

    return fig, ax


