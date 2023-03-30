"""Functions for point analysis."""

import numpy as np
import pandas as pd
from libpysal.weights import KNN, Queen, Rook
from pysal.explore import esda
from spreg import OLS, ML_Error, ML_Lag


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


def calculate_spatial_lag(
    data, y_col_name, weights_matrix, ID_column_name, transform="R",
):
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

    data["lag"] = weights_matrix.sparse * data[y_col_name].values

    spatial_lag = data[[y_col_name, "lag", "geometry"]]

    return spatial_lag


def calculate_morans_I(
    data, y_col_name, weights_matrix, permutations=999, transform="R",
):
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

    moran = esda.moran.Moran(
        data[y_col_name], weights_matrix, permutations=permutations,
    )

    return moran


def prepare_data_for_spatial_regression(
    crime_data,
    explanatory_data,
    population,
    crime_col_name,
    population_col_name,
    ID_col_name,
    standardize=True,
):

    db = crime_data[[ID_col_name, crime_col_name]].merge(
        explanatory_data.drop("geometry", axis=1), on=ID_col_name,
    )
    db = db.merge(population[[ID_col_name, population_col_name]], on=ID_col_name)
    db[f"{crime_col_name}_rate"] = db[crime_col_name] / db[population_col_name]

    if standardize:
        db_num = db.select_dtypes(include="number")
        db_num = (db_num - db_num.mean()) / db_num.std()
        db[db_num.columns] = db_num

    # introduce "geometry" column
    db = db.merge(explanatory_data[["GSS_CODE", "geometry"]], on="GSS_CODE")

    return db


def perform_non_spatial_regression(db, y_var_name, x_var_names):
    """Perform non-spatial regression.

    Parameters:
    -----------
    db: geopandas.GeoDataFrame
        GeoDataFrame containing the data to be used for performing non-spatial regression.
    x_var_names: str
        Name of the column containing the dependent variable.
    x_var_names: list
        List of names of the independent variables.

    Returns:
    --------
    model: spreg.ols.OLS

    """
    return OLS(
        # Dependent variable
        db[[y_var_name]].values,
        # Independent variables
        db[x_var_names].values,
        # Dependent variable name
        name_y=y_var_name,
        # Independent variable name
        name_x=x_var_names,
        white_test=True,
    )


def perform_spatial_regression(db, y_var_name, x_var_names, method="OLS"):
    """Perform spatial regression.

    Parameters:
    -----------
    db: geopandas.GeoDataFrame
        GeoDataFrame containing the data to be used for performing spatial regression.
    y_var_col_name: str
        Name of the column containing the dependent variable.
    y_name: str
        Name of the dependent variable.
    independent_variable_names: list
        List of names of the independent variables.
    method: str
        Method to be used for performing spatial regression. Options are:
        - "OLS"
        - "ML_Lag"
        - "ML_Error"

    Returns:
    --------
    model: spreg.ols.OLS
        Spatial regression model.

    """
    assert y_var_name in db.columns, f"Column {y_var_name} not found in the database."
    assert all(
        x_var_name in db.columns for x_var_name in x_var_names
    ), "All specified columns in 'x_var_name' are not found in the database."

    W = create_weights_matrix(db, method="knn", k=8)

    # Row-standardize W
    W.transform = "r"

    y = db[[y_var_name]].values

    x = np.array([db[col] for col in x_var_names]).T
    x_name = x_var_names

    if method == "OLS":
        model = OLS(
            y=y,
            x=x,
            w=W,
            name_y=y_var_name,
            name_x=x_name,
            name_w="W",
            name_ds="Burglary_VS_IMDScores",
            white_test=True,
            spat_diag=True,
            moran=True,
        )

    elif method == "ML_Lag":
        model = ML_Lag(
            y=y,
            x=x,
            w=W,
            name_y=y_var_name,
            name_x=x_name,
            name_w="W",
            name_ds="Burglary_VS_IMDScores",
        )

    elif method == "ML_Error":
        model = ML_Error(
            y=y,
            x=x,
            w=W,
            name_y=y_var_name,
            name_x=x_name,
            name_w="W",
            name_ds="Burglary_VS_IMDScores",
        )

    else:
        raise ValueError(
            "Invalid method. Valid options are: 'OLS', 'ML_Lag', 'ML_Error'.",
        )

    return model


def get_reg_summary(model, method):
    x_vars = pd.Series(data=model.name_x, name="Independent Variable")
    betas = pd.Series(data=model.betas.ravel(), name="Coefficient")

    betas = pd.Series(data=model.std_err, name="Std. Error")

    if method == "OLS":
        tstat_temp, prob_temp = zip(*model.t_stat)
        stat = pd.Series(data=list(tstat_temp), name="t-Statistic")
        prob = pd.Series(data=list(prob_temp), name="Probabilty")

    elif method in ["ML_Error", "ML_Lag"]:

        zstat_temp, prob_temp = zip(*model.z_stat)
        stat = pd.Series(data=list(zstat_temp), name="z-Statistic")
        prob = pd.Series(data=list(prob_temp), name="Probabilty")

    reg_summary = pd.concat([x_vars, betas, stat, prob], axis=1)
    reg_summary["Dependent Variable"] = model.name_y

    return reg_summary


def get_spatial_diagnostics(model):
    lm_error = pd.Series(
        {"Value": model.lm_error[0], "p-value": model.lm_error[1]},
        name="Lagrange Multiplier (error)",
    )

    lm_lag = pd.Series(
        {"Value": model.lm_lag[0], "p-value": model.lm_lag[1]},
        name="Lagrange Multiplier (lag)",
    )

    rlm_error = pd.Series(
        {"Value": model.rlm_error[0], "p-value": model.rlm_error[1]},
        name="Robust LM (error)",
    )

    rlm_lag = pd.Series(
        {"Value": model.rlm_lag[0], "p-value": model.rlm_lag[1]}, name="Robust LM (lag)",
    )

    morans_i = pd.Series(
        {"Value": model.moran_res[0], "p-value": model.moran_res[2]}, name="Moran's I",
    )

    return pd.concat([lm_error, lm_lag, rlm_error, rlm_lag, morans_i], axis=1)
