import logging
from collections import defaultdict

import numpy as np
from darts import TimeSeries
from darts.dataprocessing.transformers import Scaler
from darts.models.forecasting.forecasting_model import ForecastingModel
from numpy import average
from pandas import Timedelta
from tqdm import tqdm

from time_series_model.emission_factors import EMISSION_FACTORS

logger = logging.getLogger(__name__)


def get_covariate_args(model: ForecastingModel, covariates: TimeSeries):
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


def cross_validation_without_refit(
    model: ForecastingModel,
    prefix_series: TimeSeries,
    test_series: TimeSeries,
    metrics: dict[str, callable],
    data_scaler: Scaler | None,
    covariates: dict[str, TimeSeries],
    max_n_split: int = 5,
    forecast_horizon: int = 7 * 24,
) -> dict[str, float]:
    """Perform cross-validation without refitting the model.

    Parameters
    ----------
    model
        The forecasting model to be evaluated.
    prefix_series
        The time series directly preceding the test series.
    test_series
        The time series to be used for evaluation.
    metrics
        A dict of metric functions for evaluating forecast accuracy.
    data_scaler
        The scaler used for rescaling the data.
    max_n_split
        Maximal number of splits for cross-validation. Default is 5.
    covariates
        Dictionary of covariates to be used during evaluation.
    forecast_horizon
        Forecast horizon in hours, i.e. the size of intervals the model will be tested on. Default is 7 * 24.

    Returns
    -------
    metrics_dict | None
        A dictionary with average values of every metric in `metrics` or `None` in an error case.
    """

    assert forecast_horizon > 0, "`forecast_horizon` must be bigger than 0."
    assert (
        prefix_series.end_time() + Timedelta(hours=1) == test_series.start_time()
    ), f"The series must be continuous but prefix ends at {prefix_series.end_time()} and test starts at {test_series.start_time()}."

    start = prefix_series.end_time()
    full_series = prefix_series.concatenate(test_series)

    # Calculate the ranges, i.e. the ranges on which to test the model
    n_split = len(test_series[start:]) // forecast_horizon
    ranges = [
        (start + Timedelta(hours=forecast_horizon * i), start + Timedelta(hours=forecast_horizon * (i + 1)))
        for i in range(n_split)
    ]
    ranges = [(start, end) for start, end in ranges if end <= full_series.end_time()]
    if max_n_split <= len(ranges):
        ranges = ranges[:max_n_split]
    else:
        logger.info(f'The split size was changed from {max_n_split} to {len(ranges)}')

    # Get covariates
    _, covariate_args_inference = get_covariate_args(model, covariates)

    # Calculate per split
    metrics_dict = defaultdict(list)
    for start, end in tqdm(ranges):
        # Run model prediction
        forecast = model.predict(
            forecast_horizon, series=full_series[:start], **covariate_args_inference, verbose=False
        )

        # Rescale forecast and original data
        forecast_rescaled = None
        original_rescaled = None
        if isinstance(data_scaler, Scaler):
            forecast_rescaled = data_scaler.inverse_transform(forecast)
            original_rescaled = data_scaler.inverse_transform(full_series[forecast.start_time():forecast.end_time()])
        # When using VARIMA there's no need to pass a data scaler to the evaluation function
        if data_scaler is None:
            forecast_rescaled = forecast
            original_rescaled = full_series[forecast.start_time():forecast.end_time()]

        # Calculate metrics
        for name, metric in metrics.items():
            metrics_dict[name].append(metric(original_rescaled, forecast_rescaled))

    for metric, results in metrics_dict.items():
        metrics_dict[metric] = average(results)

    metrics_dict = dict(metrics_dict)
    return metrics_dict


def co2_rmse(
    original: TimeSeries,
    forecast: TimeSeries,
    disable_weights: bool = False,
) -> float:
    """Calculate the RMSE of CO2 emissions.

    Parameters
    ----------
    original
        The original time series.
    forecast
        The forecasted time series.

    Returns
    -------
    float
        The RMSE of CO2 emissions.
    """

    assert original.start_time() == forecast.start_time(), "Start times must be equal."
    assert original.end_time() == forecast.end_time(), "End times must be equal."
    assert list(original.columns) == list(forecast.columns), "Columns must be equal."

    names = list(original.columns)
    y_true = original.values()
    y_pred = forecast.values()

    assert (
        len(EMISSION_FACTORS.values()) == y_true.shape[1] == y_pred.shape[1]
    ), "Number of emission factors must be equal to number of columns."

    # Weighted RMSE
    # Calculate difference between true and predicted values
    if not disable_weights:
        weights = np.array([EMISSION_FACTORS[name] for name in names])
        diff = weights * (y_true - y_pred)
    else:
        diff = y_true - y_pred
    # Calculate RMSE, make sure to average over time axis only
    mse = np.mean(diff**2, axis=0)
    rmse = np.sqrt(mse)
    # Average over all energy resources
    rmse = np.mean(rmse)

    return rmse
