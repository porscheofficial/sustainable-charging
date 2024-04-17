import logging

import pandas as pd
from darts import TimeSeries

from model import config, util

logger = logging.getLogger(__name__)


def load() -> TimeSeries:
    """
    Loads data from the specified file paths and concatenates them into a single DataFrame.
    """
    logger.info("Initiating data loading process...")
    data_wind = pd.read_csv(config.WEATHER_DATA_WIND_PATH, delimiter=",")
    data_solar = pd.read_csv(config.WEATHER_DATA_SOLAR_PATH, delimiter=",")
    assert data_wind.shape[0] == data_solar.shape[0], (
        "The number of rows in the two weather data " "files must be equal."
    )

    # Rename time column to timestamp
    data_wind = data_wind.rename(columns={"time": "timestamp"})
    data_solar = data_solar.rename(columns={"time": "timestamp"})

    # Get relevant columns for each type of weather data
    data_wind = data_wind[config.WIND_COLUMNS + ["timestamp"]]
    data_solar = data_solar[config.SOLAR_COLUMNS + ["timestamp"]]

    # Merge the two DataFrames
    data = pd.merge(data_wind, data_solar, on="timestamp")

    # Convert timestamp to datetime
    data["timestamp"] = pd.to_datetime(data["timestamp"])

    # Avoid any missing values
    missing_values = data.isnull().sum()
    assert missing_values.sum() == 0, (
        f"There are missing values in the weather data. "
        f"Missing values: {missing_values}"
    )

    # Pytorch throws an error on M1/M2 Macbooks with float64
    for column in data.select_dtypes(include=["float64"]).columns:
        data[column] = data[column].astype("float32")

    # Log results
    logger.info("Has weather data with")
    logger.info("  shape: %s", data.shape)
    logger.info("  columns: %s", data.columns)

    # Convert to TimeSeries
    data = util.convert_df_to_time_series(data)

    return data
