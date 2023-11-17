from darts.metrics.metrics import rmse, coefficient_of_variation, mape
from darts.models.forecasting.forecasting_model import ForecastingModel
from darts import TimeSeries


def eval_model(
        model: ForecastingModel,
        train_series: TimeSeries,
        validation_series: TimeSeries,
        n_split: int = 5) -> float:
    pass
