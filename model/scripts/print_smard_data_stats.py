import pandas as pd
from darts import TimeSeries

from model.config import EMISSION_FACTORS
from model.data.smard import load as load_smard_data
from model.util import convert_df_to_time_series


def main():
    # Load
    train, val, test = load_smard_data()
    full = convert_df_to_time_series(
        pd.concat([train.pd_dataframe(), val.pd_dataframe(), test.pd_dataframe()]).reset_index()
    )

    for split, data in zip(["train", "val", "test", "full"], [train, val, test, full]):
        print(f"Split: {split}")
        print(f"  start: {data.start_time()}")
        print(f"  end: {data.end_time()}")

        # Apply co2 factors
        data_co2 = data.pd_dataframe()
        for name, factor in EMISSION_FACTORS.items():
            data_co2[name] = data_co2[name] * factor
        data_sum = data_co2.sum(axis=1)

        print("  kgCO2e data")
        print("    mean:", data_sum.mean())
        print("    std:", data_sum.std())


if __name__ == "__main__":
    main()
