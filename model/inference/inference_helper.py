import argparse
from dataclasses import dataclass

import joblib
import optuna
from darts import TimeSeries
from darts.dataprocessing.transformers import Scaler
from darts.metrics import rmse
from darts.models import RNNModel, XGBModel
from darts.models.forecasting.forecasting_model import ForecastingModel

from model import config, data, evaluation, feature_engineering
from model.feature_engineering import get_covariates_time
from model.util import get_covariate_args_for_model


@dataclass
class DataRequirementInfo:
    smard_data_lookback: int
    weather_data_lookback: int
    weather_data_lookahead: int
    smard_data_columns: list[str]
    weather_data_columns: list[str]


class InferenceHelper:
    def __init__(self, model_dir: str):
        self.model_dir = model_dir

        # Load model from file
        self.model = RNNModel(
            model="LSTM",
            hidden_dim=64,
            n_rnn_layers=3,
            dropout=0.028777667213468805,
            training_length=424,
            input_chunk_length=212,
            n_epochs=5,
        )
        self.model = self.model.load(self.model_dir + "/model")
        # self.model.load_from_checkpoint(self.model_dir) + "/model.ckpt"
        self.scaler = Scaler()
        self.scaler = joblib.load(self.model_dir + "/scaler_smard")

    def get_data_request_info(self, n_steps_ahead: int) -> DataRequirementInfo:
        return DataRequirementInfo(
            smard_data_lookback=self.model.input_chunk_length,
            weather_data_lookback=self.model.input_chunk_length,
            weather_data_lookahead=n_steps_ahead,
            smard_data_columns=[
                "biomass_mwh",
                "hydropower_mwh",
                "wind_offshore_mwh",
                "wind_onshore_mwh",
                "photovoltaic_mwh",
                "other_renewables_mwh",
                "nuclear_mwh",
                "brown_coal_mwh",
                "hard_coal_mwh",
                "natural_gas_mwh",
                "pumped_storage_mwh",
                "other_conventional_mwh",
            ],
            weather_data_columns=["wspd", "pres", "temp", "tsun", "prcp"],
        )

    def predict(self, smard_data: TimeSeries, weather_data: TimeSeries, n_steps_ahead: int) -> TimeSeries:
        covariates_time = get_covariates_time(weather_data)
        covariates = weather_data.stack(covariates_time)
        _, covariate_args_inference = get_covariate_args_for_model(self.model, covariates)
        result = self.model.predict(n_steps_ahead, series=smard_data, **covariate_args_inference, verbose=False)
        result = self.scaler.inverse_transform(result)
        return result
