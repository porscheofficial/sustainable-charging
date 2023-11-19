import pytest
import os

from darts.dataprocessing.transformers import Scaler
from darts.models.forecasting.rnn_model import RNNModel
from darts.metrics.metrics import rmse
import pandas as pd
from darts import TimeSeries
from darts.utils.timeseries_generation import datetime_attribute_timeseries

from ..src.evaluation_method import cross_validation_without_refit


@pytest.mark.parametrize(
    'model_file_path',
    [
        os.path.join(os.path.dirname(__file__), '..', 'models', 'lstm_model_preliminary.pkl'),
    ]
)
def test_evaluation_method(model_file_path):
    data = pd.read_parquet(os.path.join(os.path.dirname(__file__), '..', 'data', 'processed', 'energy_data_processed.parquet'))
    data.set_index("timestamp", inplace=True)
    data = data[data.columns].astype(float)
    series = TimeSeries.from_dataframe(data, fill_missing_dates=True, fillna_value=0)

    data_scaler = Scaler()
    series = data_scaler.fit_transform(series)

    val_split = 0.3
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
    cross_validation_without_refit(
        model=model,
        series=validation_series,
        start=validation_series.start_time(),
        metrics=[rmse],
        data_scaler=data_scaler,
        covariates=covariates
    )
