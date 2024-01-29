from pprint import pprint

import numpy as np
import pandas as pd
import torch

from model.inference.inference_helper import InferenceHelper
from model.util import convert_df_to_time_series


def main():
    assert not torch.cuda.is_available(), "We want to run this on CPU only."

    # Load model
    m = InferenceHelper("model_results/lstm")

    # Get data requirements for model inference
    data_req = m.get_data_request_info(7 * 24)  # Data requirements for 7d ahead prediction
    pprint(data_req)

    # Create random data. This should be replaced with real data that is fetched from the APIs
    n_smard_datapoints = data_req.smard_data_lookback
    n_weather_datapoints = data_req.weather_data_lookback + data_req.weather_data_lookahead
    random_smard_data = pd.DataFrame(
        np.random.rand(n_smard_datapoints, len(data_req.smard_data_columns)).astype(np.float32),
        columns=data_req.smard_data_columns,
    )
    random_weather_data = pd.DataFrame(
        np.random.rand(n_weather_datapoints, len(data_req.weather_data_columns)).astype(np.float32),
        columns=data_req.weather_data_columns,
    )
    # Make sure we have timestamp columns
    now = pd.Timestamp.now()
    random_smard_data["timestamp"] = pd.date_range(
        start=now - pd.Timedelta(hours=n_smard_datapoints), periods=n_smard_datapoints, freq="H"
    )
    random_weather_data["timestamp"] = pd.date_range(
        start=now - pd.Timedelta(hours=data_req.weather_data_lookback),
        periods=n_weather_datapoints,
        freq="H",
    )
    # Convert to timeseries
    random_smard_data = convert_df_to_time_series(random_smard_data)
    random_weather_data = convert_df_to_time_series(random_weather_data)

    # Print data
    print("SMARD data:")
    print(random_smard_data)
    print("Weather data:")
    print(random_weather_data)

    # Predict
    prediction = m.predict(random_smard_data, random_weather_data, 7 * 24)
    print("Prediction:")
    print(prediction)


if __name__ == "__main__":
    main()
