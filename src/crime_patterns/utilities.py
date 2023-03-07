"""Utilities used in various parts of the project."""

import yaml
import pandas as pd
import geopandas as gpd

def read_yaml(path):
    """Read a YAML file.

    Args:
        path (str or pathlib.Path): Path to file.

    Returns:
        dict: The parsed YAML file.

    """
    with open(path) as stream:
        try:
            out = yaml.safe_load(stream)
        except yaml.YAMLError as error:
            info = (
                "The YAML file could not be loaded. Please check that the path points "
                "to a valid YAML file."
            )
            raise ValueError(info) from error
    return out
    
def convert_points_df_to_gdf(df, longitude_column_name="Longitude", latitude_column_name="Latitude", crs="EPSG:4326"):

    assert longitude_column_name in df.columns, f"{longitude_column_name}, not found in Dataframe columns."
    assert latitude_column_name in df.columns, f"{latitude_column_name}, not found in Dataframe columns."

    geometry = gpd.points_from_xy(x = df[longitude_column_name], y = df[latitude_column_name], crs=crs)

    return gpd.GeoDataFrame(data=df, geometry=geometry)
