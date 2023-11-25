import os

import pytest
from darts.dataprocessing.transformers.scaler import Scaler
from darts.metrics.metrics import rmse, coefficient_of_variation
from darts.models.forecasting.rnn_model import RNNModel
from darts.timeseries import TimeSeries
from darts.utils.timeseries_generation import datetime_attribute_timeseries
from pandas import Timedelta
from pandas import read_parquet

from time_series_model.src.evaluation_method import cross_validation_without_refit


@pytest.fixture(scope='module')
def setup():
    model_file_path = os.path.join(os.path.dirname(__file__), 'test_models', 'test_lstm_model.pkl')

    data = read_parquet(os.path.join(os.path.dirname(__file__), 'test_data', 'processed_data_5000_rows.parquet'))
    data.set_index("timestamp", inplace=True)
    data = data[data.columns].astype(float)
    series = TimeSeries.from_dataframe(data, fill_missing_dates=True, fillna_value=0)

    data_scaler = Scaler()
    series = data_scaler.fit_transform(series)

    val_split = 0.7
    train_end_index = (1 - val_split) * len(series)
    train_end_index = int(train_end_index)
    validation_series = series[train_end_index:]

    weekday = datetime_attribute_timeseries(series, attribute="weekday")
    month = datetime_attribute_timeseries(series, attribute="month")
    hour = datetime_attribute_timeseries(series, attribute="hour")
    covariates = weekday.stack(hour).stack(month)

    scaler_covariates = Scaler()
    covariates = scaler_covariates.fit_transform(
        covariates
    )

    model = RNNModel.load(model_file_path)

    return model, validation_series, data_scaler, covariates


@pytest.mark.parametrize(
    'start_delta, metrics, max_n_split, forecast_horizon, plotting, expected_result',
    [
        (0, [rmse], 2, 7 * 24, False, None),
        (167, [rmse, coefficient_of_variation], 1, 7 * 24, False,
         {'coefficient_of_variation': 43.45621093238546, 'rmse': 1656.2597046492676}),
        (166, [rmse], 3, 7 * 24, False, None),
        (167, [rmse], 2, 1, False, {'rmse': 2014.2852136265383}),
        (167, [rmse], 2, 0, False, None)
    ]
)
def test_evaluation_method(setup, start_delta, metrics, max_n_split, forecast_horizon, plotting, expected_result):
    model, validation_series, data_scaler, covariates = setup

    metrics_dict = cross_validation_without_refit(
        model=model,
        series=validation_series,
        start=validation_series.start_time() + Timedelta(start_delta, 'h'),
        metrics=metrics,
        data_scaler=data_scaler,
        covariates=covariates,
        max_n_split=max_n_split,
        forecast_horizon=forecast_horizon,
        plotting=plotting
    )

    assert metrics_dict == expected_result
