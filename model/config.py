import os

# Train/Val/Test Split
TRAIN_END_DATE = "2022-03-05"
VAL_END_DATE = "2023-03-05"

# IDs we are using for weather data
SOLAR_IDS = [10513, 10382, 10637, 10147, 10469, 10852, 10763, 10738, 10338]
WIND_IDS = [10224, 10291, 10113, 10035, 10264, 10430]

# Path to the relevant data
RAW_DATA_PATH = "."
SMARD_DATA_PATHS = [
    os.path.join(RAW_DATA_PATH, "data/raw/2015_2016.csv"),
    os.path.join(RAW_DATA_PATH, "data/raw/2017_2018.csv"),
    os.path.join(RAW_DATA_PATH, "data/raw/2019_2020.csv"),
    os.path.join(RAW_DATA_PATH, "data/raw/2021_2022.csv"),
    os.path.join(RAW_DATA_PATH, "data/raw/2022_2023.csv"),
]
WEATHER_DATA_SOLAR_PATH = os.path.join(RAW_DATA_PATH, "data/raw/weather_data_solar_stations.csv")
WEATHER_DATA_WIND_PATH = os.path.join(RAW_DATA_PATH, "data/raw/weather_data_wind_stations.csv")

# Smard data columns are renamed to be more readable
SMARD_COLUMN_RENAMES = {
    "Timestamp": "timestamp",
    "Biomasse [MWh] Berechnete Auflösungen": "biomass_mwh",
    "Wasserkraft [MWh] Berechnete Auflösungen": "hydropower_mwh",
    "Wind Offshore [MWh] Berechnete Auflösungen": "wind_offshore_mwh",
    "Wind Onshore [MWh] Berechnete Auflösungen": "wind_onshore_mwh",
    "Photovoltaik [MWh] Berechnete Auflösungen": "photovoltaic_mwh",
    "Sonstige Erneuerbare [MWh] Berechnete Auflösungen": "other_renewables_mwh",
    "Kernenergie [MWh] Berechnete Auflösungen": "nuclear_mwh",
    "Braunkohle [MWh] Berechnete Auflösungen": "brown_coal_mwh",
    "Steinkohle [MWh] Berechnete Auflösungen": "hard_coal_mwh",
    "Erdgas [MWh] Berechnete Auflösungen": "natural_gas_mwh",
    "Pumpspeicher [MWh] Berechnete Auflösungen": "pumped_storage_mwh",
    "Sonstige Konventionelle [MWh] Berechnete Auflösungen": "other_conventional_mwh",
}

# Weather data columns that we use
WIND_COLUMNS = ["wspd", "pres", "temp"]
SOLAR_COLUMNS = ["tsun", "prcp"]

# Grouping of energy sources
RENEWABLE_ENERGY_SOURCES = [
    "biomass_mwh",
    "hydropower_mwh",
    "wind_offshore_mwh",
    "wind_onshore_mwh",
    "photovoltaic_mwh",
    "other_renewables_mwh",
]
NON_RENEWABLE_ENERGY_SOURCES = [
    "nuclear_mwh",
    "brown_coal_mwh",
    "hard_coal_mwh",
    "natural_gas_mwh",
    "pumped_storage_mwh",
    "other_conventional_mwh",
]

# Emission factors in kg CO2e/MWh
EMISSION_FACTORS = {
    "biomass_mwh": 485.0,
    "hydropower_mwh": 24.0,
    "wind_offshore_mwh": 12.0,
    "wind_onshore_mwh": 11.0,
    "photovoltaic_mwh": 38.666666666666664,
    "nuclear_mwh": 12.0,
    "brown_coal_mwh": 820.0,
    "hard_coal_mwh": 820.0,
    "natural_gas_mwh": 490.0,
    "pumped_storage_mwh": 20.5,
    "other_conventional_mwh": 655.0,
    "other_renewables_mwh": 38.0,
}

N_OPTUNA_TRIALS = 10
