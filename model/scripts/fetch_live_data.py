from datetime import datetime, timedelta

from model.inference.weather import fetch_weather_data
from model.inference.smard import fetch_smard_data
from model.inference.inference_helper import DataRequirementInfo

from model.util import convert_df_to_time_series


def fetch(data_req: DataRequirementInfo):
    smard_data = fetch_smard_data(n_lookback=data_req.smard_data_lookback)
    last_timestamp = smard_data["timestamp"].max()

    weather_data = fetch_weather_data(
        last_timestamp,
        n_lookback=data_req.weather_data_lookback,
        n_lookahead=data_req.weather_data_lookahead,
    )

    smard_data = convert_df_to_time_series(smard_data)
    weather_data = convert_df_to_time_series(weather_data)

    return smard_data, weather_data


def main():
    data_req = DataRequirementInfo(
        smard_data_lookback=212,
        weather_data_lookback=212,
        weather_data_lookahead=24 * 7,
        smard_data_columns=[
            "biomass_mwh",
            "hydropower_mwh",
            "wind_offshore_mwh",
            "wind_onshore_mwh",
            "photovoltaic_mwh",
            "other_renewables_mwh",
            "nuclear_mwh",
            "brown_coal_mwh",
            "hard_coal_mwh",
            "natural_gas_mwh",
            "pumped_storage_mwh",
            "other_conventional_mwh",
        ],
        weather_data_columns=["wspd", "pres", "temp", "tsun", "prcp"],
    )

    print(fetch(data_req=data_req))


if __name__ == "__main__":
    main()
