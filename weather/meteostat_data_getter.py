from datetime import datetime
from meteostat import Hourly

start = datetime(2015, 1, 1)
end = datetime(2023, 11, 22)

solar_stations_data = Hourly([10513, 10382, 10637, 10147, 10469, 10852, 10763, 10738, 10338], start, end)
solar_stations_data = solar_stations_data.normalize() 
solar_stations_data = solar_stations_data.aggregate('1H', spatial=True)	
solar_stations_data = solar_stations_data.fetch()

solar_stations_data.to_csv('weather_data_solar_stations.csv')

wind_stations_data = Hourly([10224, 10291, 10113, 10035, 10264, 10430], start, end)
wind_stations_data = wind_stations_data.normalize() 
wind_stations_data = wind_stations_data.aggregate('1H', spatial=True)	
wind_stations_data = wind_stations_data.fetch()

wind_stations_data.to_csv('weather_data_wind_stations.csv')
