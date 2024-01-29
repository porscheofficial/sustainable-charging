from dataclasses import dataclass

from darts import TimeSeries

from model.data.smard import load as load_smard_data
from model.data.weather import load as load_weather_data


@dataclass
class Dataset:
    train: TimeSeries
    val: TimeSeries
    test: TimeSeries
    weather: TimeSeries


def load():
    train, val, test = load_smard_data()
    weather = load_weather_data()

    return Dataset(train=train, val=val, test=test, weather=weather)
