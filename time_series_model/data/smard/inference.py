import logging
import requests
import pandas as pd
from datetime import datetime, timedelta
from darts import TimeSeries

logger = logging.getLogger(__name__)

def get_week_start_dates_until_cutoff(cutoff_date):
    """ Returns a list of the start dates of weeks from now until the given cutoff date at 00:00:00 """
    current_date = datetime.now()
    current_date = current_date.replace(hour=0, minute=0, second=0, microsecond=0)  # Start from beginning of today
    week_starts = []

    while current_date >= cutoff_date:
        weekday = current_date.weekday()
        start_of_week = current_date - timedelta(days=weekday)
        start_of_week = start_of_week.replace(hour=0, minute=0, second=0, microsecond=0)

        if start_of_week not in week_starts:
            week_starts.append(start_of_week)

        current_date -= timedelta(days=7)  # Move back one week

    return week_starts

def fetch_smard_data(cutoff_date):
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

    call_counter = 1
    filter_codes = {
        'biomass_mwh': 4066,
        'hydropower_mwh': 1226,
        'wind_offshore_mwh': 1225,
        'wind_onshore_mwh': 4067,
        'photovoltaic_mwh': 4068,
        'other_renewables_mwh': 1228,
        'nuclear_mwh': 1224,
        'brown_coal_mwh': 1223,
        'hard_coal_mwh': 4069,
        'natural_gas_mwh': 4071,
        'pumped_storage_mwh': 4070,
        'other_conventional_mwh': 1227
    }

    week_start_dates = get_week_start_dates_until_cutoff(cutoff_date)
    all_data_frames = []

    for week_start_date in week_start_dates:
        week_start_timestamp = int(week_start_date.timestamp() * 1000)  # Convert to milliseconds

        weekly_data = {}
        for energy, code in filter_codes.items():
            url = f'https://smard.api.proxy.bund.dev/app/chart_data/{code}/DE/{code}_DE_hour_{week_start_timestamp}.json'
            headers = {'accept': 'application/json'}

            response = requests.get(url, headers=headers)
            logger.info(f"Call {call_counter}: {url}")
            call_counter += 1
            if response.status_code == 200:
                response_data = response.json()
                series = response_data["series"]
                if 'timestamp' not in weekly_data:
                    weekly_data['timestamp'] = [x[0] for x in series]
                weekly_data[energy] = [x[1] for x in series]
            else:
                logger.error(f"Error fetching data for {energy}: Status code {response.status_code}")

        weekly_df = pd.DataFrame(weekly_data)
        weekly_df['timestamp'] = pd.to_datetime(weekly_df['timestamp'], unit='ms')
        weekly_df.set_index('timestamp', inplace=True)
        all_data_frames.append(weekly_df)

    # Concatenate all weekly data frames
    full_df = pd.concat(all_data_frames)

    # Convert to Darts TimeSeries
    ts = TimeSeries.from_dataframe(full_df)

    return ts