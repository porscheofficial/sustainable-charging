#!/usr/bin/env python

import sys
import os

sys.path.append(os.path.join(os.getcwd(), os.pardir, "time_series_model"))
sys.path.append("/hpi/fs00/home/nick.bessin/hpi-porsche-challenge")

import logging
import torch
import random
from functools import partial
import time

import optuna
import os
import pandas as pd
import numpy as np
from darts.utils.timeseries_generation import datetime_attribute_timeseries
from pandas import DataFrame

from darts import TimeSeries
from darts.models import VARIMA
from darts.metrics import rmse
from darts.dataprocessing.transformers import Scaler

from time_series_model.data.weather.weather_dataloader import MeteostatDataLoader
from time_series_model.data.data_loading import SMARDDataLoader
from time_series_model.evaluation import (
    get_covariate_args,
    cross_validation_without_refit,
    co2_rmse,
)

import warnings

warnings.filterwarnings("ignore")

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

MAX_SPLIT = 10
FORECAST_HORIZON = 7 * 24
LAST_N_SAMPLES = 16 * 168
WEATHER_INCLUDED = True


def load_smard_data():
    smard_dataloader = SMARDDataLoader(
        file_paths=[
            os.path.join(os.getcwd(), os.pardir, "data", "raw", "2015_2016.csv"),
            os.path.join(os.getcwd(), os.pardir, "data", "raw", "2017_2018.csv"),
            os.path.join(os.getcwd(), os.pardir, "data", "raw", "2019_2020.csv"),
            os.path.join(os.getcwd(), os.pardir, "data", "raw", "2021_2022.csv"),
            os.path.join(os.getcwd(), os.pardir, "data", "raw", "2022_2023.csv"),
        ]
    )
    smard_dataloader.load_data()
    smard_dataloader.preprocess_data()
    smard_dataloader.validate_data()

    return (
        smard_dataloader.get_dataframe("train"),
        smard_dataloader.get_dataframe("validation"),
        smard_dataloader.get_dataframe("test"),
    )


def convert_df_to_time_series_object(df: DataFrame):
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    df = df.set_index("timestamp")
    time_series = TimeSeries.from_dataframe(
        df,
        value_cols=list(df.columns),
        fill_missing_dates=True,
        fillna_value=0,
        freq="1H",
    )

    return time_series


def load_weather_data():
    meteostat_solar_loader = MeteostatDataLoader(
        file_paths=[
            os.path.join(
                os.getcwd(), os.pardir, "data", "raw", "weather_data_solar_stations.csv"
            )
        ],
        solar=True,
    )
    meteostat_solar_loader.load_data()
    meteostat_solar_loader.preprocess_data()
    solar_data = meteostat_solar_loader.data

    meteostat_wind_loader = MeteostatDataLoader(
        file_paths=[
            os.path.join(
                os.getcwd(), os.pardir, "data", "raw", "weather_data_wind_stations.csv"
            )
        ],
        wind=True,
    )
    meteostat_wind_loader.load_data()
    meteostat_wind_loader.preprocess_data()
    wind_data = meteostat_wind_loader.data

    print("Missing values for wind")
    for col in wind_data.columns:
        print(
            f"  Column {col} has {wind_data[col].isna().mean() * 100:0.2f}% missing values"
        )
    print("Missing values for solar")
    for col in solar_data.columns:
        print(
            f"  Column {col} has {solar_data[col].isna().mean() * 100:0.2f}% missing values"
        )

    solar_data["time"] = pd.to_datetime(solar_data["time"])
    wind_data["time"] = pd.to_datetime(wind_data["time"])

    solar_data = solar_data.set_index("time")
    wind_data = wind_data.set_index("time")

    print(f"Wind data index: {wind_data.index.min()} - {wind_data.index.max()}")
    print(f"Solar data index: {solar_data.index.min()} - {solar_data.index.max()}")

    solar_data = TimeSeries.from_dataframe(
        solar_data,
        value_cols=list(solar_data.columns),
        fill_missing_dates=True,
        fillna_value=0,
        freq="1H",
    )
    wind_data = TimeSeries.from_dataframe(
        wind_data,
        value_cols=list(wind_data.columns),
        fill_missing_dates=True,
        fillna_value=0,
        freq="1H",
    )

    wind_data = wind_data.astype(np.float32)
    solar_data = solar_data.astype(np.float32)

    weather_data = solar_data.stack(wind_data)

    return weather_data


def load_time_covariates(weather_data: TimeSeries):
    weekday = datetime_attribute_timeseries(
        weather_data, attribute="weekday", dtype=np.float32
    )
    month = datetime_attribute_timeseries(
        weather_data, attribute="month", dtype=np.float32
    )
    hour = datetime_attribute_timeseries(
        weather_data, attribute="hour", dtype=np.float32
    )
    covariates_time = weekday.stack(hour).stack(month)

    scaler_covariates = Scaler()
    covariates_time = scaler_covariates.fit_transform(covariates_time)

    return covariates_time


def fit_model(
    model: VARIMA, train: TimeSeries, covariates: TimeSeries, save_model: bool = False
):
    covariate_args = get_covariate_args(
        model=model,
        covariates=covariates,
    )[0]
    model.fit(series=train, future_covariates=covariate_args["future_covariates"])
    if save_model:
        model.save(
            path=os.path.join(
                os.getcwd(),
                os.pardir,
                "models",
                f"VARIMA_weather_{str(WEATHER_INCLUDED)}_training_{str(LAST_N_SAMPLES)}",
            )
        )


def predict_model(model: VARIMA, n: int, covariates: TimeSeries):
    covariate_args = get_covariate_args(
        model=model,
        covariates=covariates,
    )[0]
    return model.predict(n=n, future_covariates=covariate_args["future_covariates"])


def objective(trial, train, validation, covariates):
    p = trial.suggest_int("p", 1, 2)
    d = trial.suggest_int("d", 0, 0)
    q = trial.suggest_int("q", 1, 2)
    trend = trial.suggest_categorical("trend", ["n", "c", None])

    logger.info(f"Trialing with {trial.params}")

    optimizing_model = VARIMA(p=p, d=d, q=q, trend=trend)

    start = time.time()
    fit_model(optimizing_model, train, covariates)
    logger.info(f"Fitting duration: {time.time() - start}")

    start = time.time()
    eval_result = cross_validation_without_refit(
        model=optimizing_model,
        prefix_series=train,
        test_series=validation,
        metrics={
            "rmse": rmse,
            "co2_rmse": co2_rmse,
        },
        data_scaler=None,
        covariates=covariates,
        max_n_split=MAX_SPLIT,
        forecast_horizon=FORECAST_HORIZON,
    )
    logger.info(f"Cross Validation duration: {time.time() - start}")

    eval_rmse = eval_result["rmse"]
    co2_eval_rmse = eval_result["co2_rmse"]
    logger.info(f"Eval RMSE: {eval_rmse}")
    logger.info(f"Eval CO2 RMSE: {co2_eval_rmse}")

    return eval_rmse


def main():
    train, validation, test = load_smard_data()
    train = convert_df_to_time_series_object(train)
    validation = convert_df_to_time_series_object(validation)
    test = convert_df_to_time_series_object(test)

    weather_data = load_weather_data()
    covariates_time = load_time_covariates(weather_data)

    adapted_train = train[-LAST_N_SAMPLES:]
    logger.info(
        f"Train start: {adapted_train.start_time()}, Train end: {adapted_train.end_time()}"
    )
    if WEATHER_INCLUDED:
        covariates = covariates_time.stack(weather_data)[adapted_train.start_time() :]
    else:
        covariates = covariates_time[adapted_train.start_time() :]

    study = optuna.create_study(direction="minimize")
    study.optimize(
        lambda trial: objective(
            trial, train=adapted_train, validation=validation, covariates=covariates
        ),
        n_trials=1,
    )

    # test set evaluation
    best_params = study.best_params
    logger.info(f"Best params: {best_params}")

    final_model = VARIMA(**best_params)

    final_train = train.append(validation)[-LAST_N_SAMPLES:]
    if WEATHER_INCLUDED:
        test_covariates = covariates_time.stack(weather_data)[
            final_train.start_time() :
        ]
    else:
        test_covariates = covariates_time[final_train.start_time() :]

    start = time.time()
    fit_model(
        model=final_model,
        train=final_train,
        covariates=test_covariates,
        save_model=False,
    )
    logger.info(f"Last training duration: {time.time() - start}")

    eval_result = cross_validation_without_refit(
        model=final_model,
        prefix_series=final_train,
        test_series=test,
        metrics={
            "rmse": rmse,
            "co2_rmse": co2_rmse,
        },
        data_scaler=None,
        covariates=test_covariates,
        max_n_split=MAX_SPLIT,
        forecast_horizon=FORECAST_HORIZON,
    )
    eval_rmse = eval_result["rmse"]
    co2_eval_rmse = eval_result["co2_rmse"]
    logger.info(f"Eval RMSE: {eval_rmse}")
    logger.info(f"Eval CO2 RMSE: {co2_eval_rmse}")


if __name__ == "__main__":
    main()
