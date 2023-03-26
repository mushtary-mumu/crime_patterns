"""Tests for the point patterns module."""
#%%
import numpy as np
import pandas as pd
import geopandas as gpd
import pytest
from crime_patterns.analysis import spatial_regression
from libpysal.weights import KNN
from shapely.geometry import Polygon, Point

DESIRED_PRECISION = 10e-2

@pytest.fixture()
def mock_crime_data():

    np.random.seed(1)

    # Get points in a grid
    data_points = np.arange(3)
    x_coords, y_coords = np.meshgrid(data_points, data_points)

    polygons = []
    # Generate polygons
    for x, y in zip(x_coords.flatten(), y_coords.flatten()):
        poly = Polygon([(x, y), (x + 1, y), (x + 1, y + 1), (x, y + 1)])
        polygons.append(poly)

    # Convert to GeoSeries
    polygons = gpd.GeoSeries(polygons)

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
    # standardize the data
    # db_num = db.select_dtypes(include='number')
    # db_num = (db_num - db_num.mean()) / db_num.std()
    # db[db_num.columns] = db_num
    
    gdf_polygons = gpd.GeoDataFrame(db, geometry=polygons)

    def _create_random_points_within_bounds(poly, number):   
    
        np.random.seed(1)
        minx, miny, maxx, maxy = poly.bounds

        x = np.random.uniform( minx, maxx, number )
        y = np.random.uniform( miny, maxy, number )

        df = pd.DataFrame()
        df['points'] = list(zip(x,y))
        df['points'] = df['points'].apply(Point)
        
        return gpd.GeoDataFrame(df, geometry='points')
    
    points = [
            _create_random_points_within_bounds(row["geometry"], int(row["crime_count"]))
            for i, row in gdf_polygons.iterrows()
            ]
    gdf_points = pd.concat(points)
    
    return {"points": gdf_points, "polygons": gdf_polygons}


@pytest.fixture()
def mock_weights_matrix(mock_crime_data):
    return KNN.from_dataframe(mock_crime_data["polygons"], k=8)

#%%
def test_calculate_morans_I(mock_crime_data, mock_weights_matrix):

    moran = spatial_regression.calculate_morans_I(mock_crime_data["polygons"], "crime_count", mock_weights_matrix)

    assert np.isclose(moran.I, -0.125, atol=DESIRED_PRECISION)


#%%

def test_perform_spatial_regression(mock_crime_data, mock_weights_matrix):

    expected_betas = np.array([[ 0.02170552],
                        [ 0.29654963],
                        [-0.01118001],
                        [-0.00112875]])
    
    model = spatial_regression.perform_spatial_regression(db=mock_crime_data["polygons"], y_var_name="crime_rate", x_var_names=["EmpScore", "IncScore", "BHSScore"], method="OLS")
 
    np.testing.assert_array_almost_equal(model.betas, expected_betas, decimal=4)
