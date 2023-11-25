import logging
import matplotlib.pyplot as plt
from darts import TimeSeries
from darts.dataprocessing.transformers import Scaler
from darts.models.forecasting.forecasting_model import ForecastingModel
from numpy import average
from pandas import Timestamp, Timedelta


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
        metrics: list[callable],
        data_scaler: Scaler,
        covariates: dict[str, TimeSeries],
        max_n_split: int = 5,
        forecast_horizon: int = 7 * 24,
        plotting: bool = False
) -> dict | None:
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
    max_n_split
        Maximal number of splits for cross-validation. Default is 5.
    plotting
        Whether to generate plots. Default is False.
    forecast_horizon
        Forecast horizon in hours. Default is 7 * 24.

    Returns
    -------
    metrics_dict | None
        A dictionary with average values of every metric in `metrics` or `None` in an error case."""
    try:
        possible_n_split = len(series[start:]) // forecast_horizon
    except ZeroDivisionError:
        print(f'`forecast_horizon` must be bigger than 0.')
        return None
    else:
        if max_n_split < possible_n_split:
            possible_n_split = max_n_split

    _, covariate_args_inference = get_covariate_args(model, covariates)
    metrics_dict = {metric.__name__: [] for metric in metrics}

    for n in range(possible_n_split):
        next_start_timestamp = start + Timedelta(forecast_horizon * n, 'h')
        try:
            forecast = model.predict(forecast_horizon, series=series[:next_start_timestamp], **covariate_args_inference,
                                     verbose=False)
        except ValueError as e:
            print(f'Can\'t predict the very first forecast_horizon of {forecast_horizon} timestamps '
                  f'as the passed start time ({start}) needs to be '
                  f'lagged by the `input_chunk_length` of the model into the future.')
            print(e)
            return None
        except Exception as e:
            print(e)
            return None

        forecast_rescaled = data_scaler.inverse_transform(forecast)
        original_rescaled = data_scaler.inverse_transform(
            series[next_start_timestamp + Timedelta(1, 'h'):forecast.end_time()])

        for metric in metrics:
            metrics_dict[metric.__name__].append(metric(original_rescaled, forecast_rescaled))

        if plotting:
            for col in forecast_rescaled.columns:
                plt.figure(figsize=(12, 1))
                forecast_rescaled[col].plot(label="forecast")
                original_rescaled[col].plot(label="original")
                plt.title(col)
                plt.show()

    for metric, results in metrics_dict.items():
        metrics_dict[metric] = average(results)

    return metrics_dict
