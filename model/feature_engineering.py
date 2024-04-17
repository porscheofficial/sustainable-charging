import numpy as np
from darts import TimeSeries
from darts.dataprocessing.transformers import Scaler
from darts.utils.timeseries_generation import datetime_attribute_timeseries


def get_covariates_time(reference_series: TimeSeries) -> TimeSeries:
    # Create time covariates
    weekday = datetime_attribute_timeseries(
        reference_series, attribute="weekday", dtype=np.float32
    )
    month = datetime_attribute_timeseries(
        reference_series, attribute="month", dtype=np.float32
    )
    hour = datetime_attribute_timeseries(
        reference_series, attribute="hour", dtype=np.float32
    )
    covariates_time = weekday.stack(hour).stack(month)

    # Always scale time covariates
    covariates_time = Scaler().fit_transform(covariates_time)

    return covariates_time


def add_rolling_mean(data: TimeSeries, lag: int):
    transformation = {
        "function": "mean",
        "mode": "rolling",
        "window": lag,
        "center": False,  # We do not want to use future data
        "min_periods": 1,
    }

    # Prepend first value, repeat it lag times, to make sure the time series is not shortened
    prepend = data.values()[0:1]
    prepend = np.repeat(prepend, lag, axis=0)
    transformed_timeseries = data.prepend_values(prepend)

    # Apply transformation
    transformed_timeseries = transformed_timeseries.window_transform(
        transforms=transformation,
        forecasting_safe=False,
        include_current=False,
        treat_na=0,
    )
    transformed_timeseries = transformed_timeseries.shift(lag)
    transformed_timeseries = transformed_timeseries.astype(data.dtype)

    transformed_timeseries = transformed_timeseries.split_after(data.end_time())[0]

    # Make sure we do not change the time index of the series
    assert (
        transformed_timeseries.start_time() == data.start_time()
    ), "Start time of transformed series must be equal to start time of original series."
    assert (
        transformed_timeseries.end_time() == data.end_time()
    ), "End time of transformed series must be equal to end time of original series."
    assert len(transformed_timeseries) == len(
        data
    ), "Length of transformed series must be equal to length of original series."

    return data.stack(transformed_timeseries)


def add_kinetic_wind_energy_simplified(weather_data: TimeSeries) -> TimeSeries:
    kinetic_wind_energy_simplified = weather_data["wspd"] ** 2 * weather_data["pres"]
    kinetic_wind_energy_simplified = (
        kinetic_wind_energy_simplified.with_columns_renamed(
            kinetic_wind_energy_simplified.columns, ["kinetic_wind_energy"]
        )
    )
    kinetic_wind_energy_simplified = kinetic_wind_energy_simplified.astype(
        weather_data.dtype
    )
    return weather_data.stack(kinetic_wind_energy_simplified)
