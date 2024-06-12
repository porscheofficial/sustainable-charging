import requests
import logging
import pytz
from datetime import datetime, timedelta

import pandas as pd
from darts import TimeSeries

from model.util import fix_float64

logger = logging.getLogger(__name__)


def get_week_start_dates_until_cutoff(n_lookback):
    """Returns a list of the start dates of weeks from now until the given cutoff date at 00:00:00"""
    timezone = pytz.timezone("Europe/Berlin")  # hard coded to Germany (for now)
    current_date = datetime.now(timezone)
    current_date = current_date.replace(
        hour=0, minute=0, second=0, microsecond=0
    )  # Start from beginning of today
    current_date -= timedelta(
        days=current_date.weekday()
    )  # Adjust current_date to the start of the current week

    cutoff_date = current_date - timedelta(hours=n_lookback)

    # Calculate the number of weeks between current_date and cutoff_date, rounding up for partial weeks
    days_diff = (current_date - cutoff_date).days
    num_weeks = days_diff // 7 + (2 if days_diff % 7 != 0 else 1)

    week_starts = []
    for i in range(num_weeks):
        week_starts.append(current_date)
        current_date -= timedelta(days=7)  # Move back one week

    return week_starts


def fetch_energy_data(session, url, energy_type):
    """
    Fetches energy data for a given energy type and URL.
    Args:
        session (requests.Session): The session object for making requests.
        url (str): The URL for the API request.
        energy_type (str): The type of energy for which data is being fetched.

    Returns:
        dict: A dictionary with timestamps and energy data if successful, None otherwise.
    """
    try:
        response = session.get(url)
        if response.status_code == 200:
            response_data = response.json()
            series = response_data["series"]
            return {
                "timestamp": [x[0] for x in series],
                energy_type: [x[1] for x in series],
            }
        else:
            logger.error(
                f"Error fetching data for {energy_type}: Status code {response.status_code}"
            )
            return {
                "timestamp": [0.0 for x in range(0, 168)],
                energy_type: [0.0 for x in range(0, 168)],
            }
            return None
    except requests.RequestException as e:
        logger.error(f"Request exception for {energy_type}: {e}")
        return None


def fetch_smard_data(n_lookback):
    """
    Fetches energy data from the SMARD API for various energy types.
    Data is fetched for each week starting from the current date back to the week of the cutoff date.
    Each API call fetches data for a specific energy type for the entire week.
    The data from all calls are combined into a single TimeSeries object.
    Args:
        cutoff_date (datetime): The date until which the energy data is fetched.
                                Data is fetched in weekly intervals up to this date.

    Returns:
        TimeSeries: A Darts TimeSeries object containing the energy data for each type.

    Example:
        >>> cutoff_date = datetime(2024, 1, 1)
        >>> energy_data_timeseries = fetch_smard_data(cutoff_date)
        # Returns a TimeSeries object with energy data up to the specified cutoff date
    """

    energy_type_to_code_mapping = {
        "biomass_mwh": 4066,
        "hydropower_mwh": 1226,
        "wind_offshore_mwh": 1225,
        "wind_onshore_mwh": 4067,
        "photovoltaic_mwh": 4068,
        "other_renewables_mwh": 1228,
        "nuclear_mwh": 1224,
        "brown_coal_mwh": 1223,
        "hard_coal_mwh": 4069,
        "natural_gas_mwh": 4071,
        "pumped_storage_mwh": 4070,
        "other_conventional_mwh": 1227,
    }

    week_start_dates = get_week_start_dates_until_cutoff(n_lookback=n_lookback)
    all_data_frames = []

    with requests.Session() as session:
        for week_start_date in week_start_dates:
            week_start_timestamp = int(
                week_start_date.timestamp() * 1000
            )  # Convert to milliseconds
            weekly_data = {}

            for energy_type, code in energy_type_to_code_mapping.items():
                url = f"https://smard.api.proxy.bund.dev/app/chart_data/{code}/DE/{code}_DE_hour_{week_start_timestamp}.json"
                energy_data = fetch_energy_data(session, url, energy_type)
                if energy_data:
                    if "timestamp" not in weekly_data:
                        weekly_data["timestamp"] = energy_data["timestamp"]
                    weekly_data[energy_type] = energy_data[energy_type]

            if weekly_data:
                weekly_df = pd.DataFrame(weekly_data)
                weekly_df["timestamp"] = pd.to_datetime(
                    weekly_df["timestamp"], unit="ms"
                )
                all_data_frames.append(weekly_df)

    # Concatenate all weekly data frames
    full_df = (
        pd.concat(all_data_frames).sort_values(by="timestamp").reset_index(drop=True)
    )

    # Find the last valid index (non-NaN row)
    last_valid_index = full_df.dropna(how="any").last_valid_index()

    # Slice the DataFrame to keep only rows up to the last valid index
    full_df = full_df.loc[:last_valid_index]

    if len(full_df) > n_lookback:
        full_df = full_df.iloc[-n_lookback:]

    full_df = fix_float64(full_df)

    return full_df


if __name__ == "__main__":
    cutoff_date = datetime(2024, 1, 23)
    energy_data_timeseries = fetch_smard_data(cutoff_date)
    print(energy_data_timeseries)
