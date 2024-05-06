import numpy as np
import pandas as pd
import torch

import joblib

import time, datetime

from model.inference.inference_helper import InferenceHelper
from model.inference.smard import fetch_smard_data
from model.inference.weather import fetch_weather_data
from model.scripts.fetch_live_data import fetch
from model.util import convert_df_to_time_series

from model.data import load


def main():
    assert not torch.cuda.is_available(), "We want to run this on CPU only."

    # Load model
    m = InferenceHelper("model_results/lstm")

    # Get data requirements for model inference
    data_req = m.get_data_request_info(
        7 * 24
    )  # Data requirements for 7d ahead prediction

    # Get data
    smard_data, weather_data = fetch(data_req)

    prediction = m.predict(smard_data, weather_data, 7 * 24)
    prediction.to_pickle("prediction_real.pkl")
    print("Prediction:", prediction)


if __name__ == "__main__":
    main()
