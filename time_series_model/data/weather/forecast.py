from datetime import datetime, timedelta
from meteostat import Hourly
from stations import solar_ids, wind_ids


def fetch_weather_data_forecast(start_date, end_date):
    """
    Fetches weather data forecasts for the given start date and number of days in the future.
    Maximum 10 days in the future.

    Args:
        start_date (datetime): The start date of the forecast.
        end_date (datetime): The end date of the forecast.

    Returns:
        dict: A dictionary containing the solar and wind weather data forecasts.

    Example:
        >>> start_date = Date.now()  # You can replace this with any date input
        >>> end_date = start_date + timedelta(days=7)
        >>> fetch_weather_data_forecast(start_date, end_date)
        {
            'solar': <pandas.DataFrame>,
            'wind': <pandas.DataFrame>
        }
    """

    solar_stations_data = Hourly(solar_ids, start_date, end_date)
    solar_stations_data = solar_stations_data.normalize() 
    solar_stations_data = solar_stations_data.aggregate('1H', spatial=True)    
    solar_stations_data = solar_stations_data.fetch()

    wind_stations_data = Hourly(wind_ids, start_date, end_date)
    wind_stations_data = wind_stations_data.normalize() 
    wind_stations_data = wind_stations_data.aggregate('1H', spatial=True)    
    wind_stations_data = wind_stations_data.fetch()

    return {
        'solar': solar_stations_data,
        'wind': wind_stations_data
    }
