"""Tests for the point patterns module."""
#%%
import numpy as np
import pytest
from crime_patterns.analysis import spatial_regression


#%%
def test_calculate_morans_I(mock_crime_polygons, mock_weights_matrix):
    moran = spatial_regression.calculate_morans_I(
        mock_crime_polygons, "crime_count", mock_weights_matrix,
    )

    assert np.isclose(moran.I, -0.125, atol=pytest.DESIRED_PRECISION)


#%%
@pytest.mark.parametrize(
    ("method", "expected_betas"),
    [
        ("OLS", np.array([[0.04301335], [0.09338169], [-0.08306777], [-0.00129602]])),
        (
            "ML_Lag",
            np.array(
                [
                    [0.04455737],
                    [0.07901801],
                    [-0.07473801],
                    [-0.00125284],
                    [-0.27019694],
                ],
            ),
        ),
        (
            "ML_Error",
            np.array(
                [[0.04413], [0.07255359], [-0.07540317], [-0.00131914], [-0.26720614]],
            ),
        ),
        ("REG", pytest.raises(ValueError)),
    ],
)
def test_perform_spatial_regression(mock_crime_polygons, method, expected_betas):
    if method in ["OLS", "ML_Lag", "ML_Error"]:
        model = spatial_regression.perform_spatial_regression(
            db=mock_crime_polygons,
            y_var_name="crime_rate",
            x_var_names=["EmpScore", "IncScore", "BHSScore"],
            method=method,
        )

        np.testing.assert_array_almost_equal(model.betas, expected_betas, decimal=2)

    else:
        with expected_betas:
            spatial_regression.perform_spatial_regression(
                db=mock_crime_polygons,
                y_var_name="crime_rate",
                x_var_names=["EmpScore", "IncScore", "BHSScore"],
                method=method,
            )
