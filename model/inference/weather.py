from datetime import datetime, timedelta

import pandas as pd
from meteostat import Hourly

from model import config
from model.util import fix_float64


def fetch_weather_data(last_timestamp, n_lookback, n_lookahead):
    """
    Fetches weather data based on the last timestamp of the smard_data.
    Args:
        last_timestamp (datetime): The last timestamp of the smard_data.
        n_lookback (int): The number of hours to look back from the last timestamp.
        n_lookahead (int): The number of hours to look ahead from the last timestamp.

    Returns:
        weather_data: A dataframe with columns "temp", "tsun", "wspd", "pres", "prcp".
    """

    start_date = last_timestamp - timedelta(hours=n_lookback)
    end_date = last_timestamp + timedelta(hours=n_lookahead)

    solar_stations_data = Hourly(config.SOLAR_IDS, start_date, end_date)
    solar_stations_data = solar_stations_data.normalize()
    solar_stations_data = solar_stations_data.aggregate("1H", spatial=True)
    solar_stations_data = solar_stations_data.fetch()

    wind_stations_data = Hourly(config.WIND_IDS, start_date, end_date)
    wind_stations_data = wind_stations_data.normalize()
    wind_stations_data = wind_stations_data.aggregate("1H", spatial=True)
    wind_stations_data = wind_stations_data.fetch()

    weather_data = pd.concat(
        [
            solar_stations_data[["temp", "tsun"]],
            wind_stations_data[["wspd", "pres", "prcp"]],
        ],
        axis=1,
    )
    weather_data = weather_data.reset_index(names=["timestamp"])

    weather_data = fix_float64(weather_data)

    return weather_data
