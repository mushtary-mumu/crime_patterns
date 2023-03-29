import pytest
import numpy as np
import pandas as pd
import geopandas as gpd
import pytest
from sklearn.datasets import make_blobs
from crime_patterns.analysis import spatial_regression
from libpysal.weights import KNN
from shapely.geometry import Polygon, Point

def pytest_configure():
    pytest.DESIRED_PRECISION = 10e-2
    pytest.minx = -0.51035607
    pytest.miny = 51.28675865
    pytest.maxx = 0.33404393 
    pytest.maxy = 51.69187697

@pytest.fixture()
def mock_crime_polygons():

    np.random.seed(1)

    data_points = np.arange(pytest.minx, pytest.maxx, 0.2)
    x_coords, y_coords = np.meshgrid(data_points, data_points)

    polygons = []
    # Generate polygons
    for x, y in zip(x_coords.flatten(), y_coords.flatten()):
        poly = Polygon([(x, y), (x + 0.2, y), (x + 0.2, y + 0.2), (x, y + 0.2)])
        polygons.append(poly)

    # Convert to GeoSeries
    polygons = gpd.GeoSeries(polygons, crs="EPSG:4326")

    db = pd.DataFrame(
                        {
                            "ID": [f"{str(i).zfill(2)}" for i in range(len(polygons))],
                            "crime_count": np.random.randint(100, 350, size=len(polygons)),
                            "pop_count": np.random.randint(15000, 45000, size=len(polygons)),
                            "EmpScore": np.random.uniform(0.039, 0.0667, size=len(polygons)),
                            "IncScore": np.random.uniform(0.054, 0.0937, size=len(polygons)),
                            "BHSScore": np.random.uniform(23.68, 26.58, size=len(polygons)),
                        }
                    )

    db["crime_rate"] = db["crime_count"] / db["pop_count"]

    return gpd.GeoDataFrame(db, geometry=polygons, crs="EPSG:4326")

@pytest.fixture()
def mock_crime_points():

    def _create_random_clusters_within_bounds(centers, n_features=3, n_samples=300, cluster_std=0.05, random_state=0):   
    
        np.random.seed(1)
        
        # x = np.random.normal(loc=loc, scale=scale, size=size)
        # y = np.random.normal(loc=loc, scale=scale, size=size)

        coords, labels_true = make_blobs(
                        n_samples=n_samples, n_features=n_features, centers=centers, cluster_std=cluster_std, random_state=random_state
                        )

        x = coords[:, 0]
        y = coords[:, 1]

        df = pd.DataFrame()
        df['points'] = list(zip(x,y))
        df['points'] = df['points'].apply(Point)
        gdf_points = gpd.GeoDataFrame(df, geometry='points', crs="EPSG:4326")
        
        return gpd.GeoDataFrame(df, geometry='points', crs="EPSG:4326")
    
    centers = [[-0.2, -0.2], [0, 0], [0.2, 0.2]] #TODO: make this dynamic depending on the total bounds of the polygons

    gdf_points = _create_random_clusters_within_bounds(centers=centers)
    
    return gdf_points

@pytest.fixture()
def mock_weights_matrix(mock_crime_polygons):
    return KNN.from_dataframe(mock_crime_polygons, k=8)