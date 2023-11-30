from dataloader import MeteostatDataLoader

weather_data = MeteostatDataLoader(["weather_data_solar_stations.csv"], solar=True)
weather_data.load_data()
weather_data.preprocess_data()