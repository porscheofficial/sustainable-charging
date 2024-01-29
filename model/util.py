import pandas as pd
from darts import TimeSeries
from darts.models.forecasting.forecasting_model import ForecastingModel


def convert_comma_str_to_float(german_number_str: str) -> float:
    """
    Converts a German number string to a float.

    Args:
        german_number_str (str): The German number string to convert.

    Returns:
        Optional[float]: The converted number as a float, or None if conversion fails.
    """
    try:
        return float(german_number_str.replace(".", "").replace(",", "."))
    except ValueError:
        return float("nan")


def fix_float64(data: pd.DataFrame) -> pd.DataFrame:
    """
    Fixes float64 columns to float32 as Pytorch throws an error on M1/M2 Macbooks with float64.
    """
    for column in data.select_dtypes(include=["float64"]).columns:
        data[column] = data[column].astype("float32")
    return data


def convert_df_to_time_series(df: pd.DataFrame):
    df = df.set_index("timestamp")
    time_series = TimeSeries.from_dataframe(
        df, value_cols=list(df.columns), fill_missing_dates=True, fillna_value=0, freq="1H"
    )

    return time_series


def get_covariate_args_for_model(model: ForecastingModel, covariates: TimeSeries):
    """
    Prepare covariate arguments for forecasting using a ForecastingModel.

    Parameters
    ----------
    model
        A ForecastingModel instance.
    covariates
        A scaled TimeSeries object containing covariate data.

    Returns
    -------
    tuple[dict[str, TimeSeries], dict[str, TimeSeries]]
        A tuple of dictionaries, where the first dictionary (covariate_args) contains
        keys related to both past and future covariates, and the second dictionary
        (covariate_args_inference) contains keys for inference purposes.

    Note
    ----
    The entire covariates TimeSeries object is added to each key in the dictionaries
    to ensure that all relevant covariate information is available during forecasting.
    This approach simplifies the handling of covariates within the Darts framework.
    """
    covariate_args = {}
    covariate_args_inference = {}
    if model.supports_past_covariates:
        covariate_args["past_covariates"] = covariates
        covariate_args["val_past_covariates"] = covariates
        covariate_args_inference["past_covariates"] = covariates
    if model.supports_future_covariates:
        covariate_args["future_covariates"] = covariates
        covariate_args["val_future_covariates"] = covariates
        covariate_args_inference["future_covariates"] = covariates

    return covariate_args, covariate_args_inference
