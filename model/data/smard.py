import logging
import pandas as pd

from model import config
from model.util import (
    convert_comma_str_to_float,
    convert_df_to_time_series,
    fix_float64,
)

logger = logging.getLogger(__name__)


def load():
    # Load data files
    data = pd.concat(
        [pd.read_csv(file, delimiter=";") for file in config.SMARD_DATA_PATHS],
        ignore_index=True,
    )

    # Preprocess data
    data = _preprocess(data)

    # Split data into sets
    train_data = data.loc[data["timestamp"] <= config.TRAIN_END_DATE]
    validation_data = data.loc[
        (data["timestamp"] > config.TRAIN_END_DATE)
        & (data["timestamp"] <= config.VAL_END_DATE)
    ]
    test_data = data.loc[data["timestamp"] > config.VAL_END_DATE]
    logger.info(
        "Data split into sets: train=%s, val=%s, test=%s",
        len(train_data),
        len(validation_data),
        len(test_data),
    )

    # Convert to darts TimeSeries
    train_data = convert_df_to_time_series(train_data)
    validation_data = convert_df_to_time_series(validation_data)
    test_data = convert_df_to_time_series(test_data)

    # Log split start and end dates
    logger.info("Data split into sets:")
    logger.info(
        "  train: %s - %s", train_data.start_time().date(), train_data.end_time().date()
    )
    logger.info(
        "  val:   %s - %s",
        validation_data.start_time().date(),
        validation_data.end_time().date(),
    )
    logger.info(
        "  test:  %s - %s", test_data.start_time().date(), test_data.end_time().date()
    )

    return (train_data, validation_data, test_data)


def _preprocess(data: pd.DataFrame) -> pd.DataFrame:
    # Convert "Datum" column to datetime
    data["Datum"] = pd.to_datetime(data["Datum"], format="%d.%m.%Y")

    # Convert "Anfang" and "Ende" columns to time
    data["Anfang"] = pd.to_datetime(data["Anfang"], format="%H:%M").dt.time
    data["Ende"] = pd.to_datetime(data["Ende"], format="%H:%M").dt.time

    # Convert energy columns to float
    energy_columns = [col for col in data.columns if "MWh" in col]
    for col in energy_columns:
        data[col] = data[col].apply(convert_comma_str_to_float)

    # Combine "Datum" and "Anfang" into a single datetime column
    data["Timestamp"] = pd.to_datetime(
        data["Datum"].astype(str) + " " + data["Anfang"].astype(str)
    )

    # Drop the "Datum", "Anfang", and "Ende" columns
    data = data.drop(columns=["Datum", "Anfang", "Ende"])

    # Reorder columns to have "Timestamp" as the first column
    data = data[["Timestamp"] + [col for col in data.columns if col != "Timestamp"]]

    # Rename the columns
    data.rename(columns=config.SMARD_COLUMN_RENAMES, inplace=True)

    # Check for missing values
    missing_values = data.isnull().sum()
    assert (
        missing_values.sum() == 0
    ), f"There are missing values in the SMARD data. Missing values: {missing_values}"

    # Some timestamps are duplicates, remove them
    data = data.drop_duplicates(subset="timestamp")

    # Fix float64 columns to float32 as Pytorch throws an error on M1/M2 Macbooks with float64
    data = fix_float64(data)

    # Reset index
    data = data.reset_index(drop=True)

    return data
