from typing import Callable, List

from darts import TimeSeries
from darts.dataprocessing.transformers import Scaler
from darts.models.forecasting.forecasting_model import ForecastingModel
from pandas import Timestamp, Timedelta
import matplotlib.pyplot as plt


def get_covariate_args(model, covariates):

    covariate_args = {}
    covariate_args_inference = {}
    if model.supports_past_covariates:
        covariate_args['past_covariates'] = covariates
        covariate_args['val_past_covariates'] = covariates
        covariate_args_inference['past_covariates'] = covariates
    if model.supports_future_covariates:
        covariate_args['future_covariates'] = covariates
        covariate_args['val_future_covariates'] = covariates
        covariate_args_inference['future_covariates'] = covariates

    return covariate_args, covariate_args_inference


def cross_validation_without_refit(
        model: ForecastingModel,
        series: TimeSeries,
        start: Timestamp,
        metrics: List[Callable],
        data_scaler: Scaler,
        covariates: dict[str, TimeSeries],
        n_split: int = 5,
        plotting: bool = False,
        forecast_horizon: int = 7 * 24
) -> None:
    """Perform cross-validation without refitting the model.

    Parameters
    ----------
    model
        The forecasting model to be evaluated.
    series
        The time series data for evaluation.
    start
        The starting timestamp for the evaluation.
    metrics
        A list of metric functions for evaluating forecast accuracy.
    data_scaler
        The scaler used for rescaling the data.
    covariates
        Dictionary of covariates to be used during evaluation.
    n_split
        Number of splits for cross-validation. Default is 5.
    plotting
        Whether to generate plots. Default is False.
    forecast_horizon
        Forecast horizon in hours. Default is 7 * 24.

    Returns
    -------
    None
        The function prints evaluation metrics for each iteration and, if plotting is enabled, displays plots."""
    for n in range(n_split, -1, -1):
        next_start_timestamp = start + Timedelta(forecast_horizon * n, 'h')
        try:
            series[next_start_timestamp]
        except:
            continue
        else:
            print(f"n_split is set to {n}")
            n_split = n
            break

    _, covariate_args_inference = get_covariate_args(model, covariates)

    for n in range(n_split):
        next_start_timestamp = start + Timedelta(forecast_horizon * n, 'h')
        forecast = model.predict(forecast_horizon, series=series[:next_start_timestamp], **covariate_args_inference,
                                 verbose=False)

        forecast_rescaled = data_scaler.inverse_transform(forecast)
        original_rescaled = data_scaler.inverse_transform(
            series[next_start_timestamp + Timedelta(1, 'h'):forecast.end_time()])

        for metric in metrics:
            calculated_metric = metric(original_rescaled, forecast_rescaled)
            print(f'{metric.__name__}: {calculated_metric}')

        if plotting:
            for col in forecast_rescaled.columns:
                plt.figure(figsize=(12, 1))
                forecast_rescaled[col].plot(label="forecast")
                original_rescaled[col].plot(label="original")
                plt.title(col)
                plt.show()
