from datetime import datetime, timedelta
import functools
import pandas as pd


CO2_COEFFICIENTS = {
    "Coal—PC": 820,
    "Gas—Combined Cycle": 490,
    "Biomass—cofiring": 740,
    "Biomass—dedicated": 230,
    "Geothermal": 38,
    "Hydropower": 24,
    "Nuclear": 12,
    "Concentrated Solar Power": 27,
    "Solar PV—rooftop": 41,
    "Solar PV—utility": 48,
    "Wind onshore": 11,
    "Wind offshore": 12,
}


def get_time_to_charge(
    battery_capacity: float,
    charging_curve: list[float],
    current_soc: int,
    target_soc: int = 80,
    efficiency: float = 0.9,
) -> float:
    """
    Get the estimated time to charge from the current state of charge (SOC) to a target SOC.

    Args:
        battery_capacity: The capacity of the battery
        charging_curve: The charging curve of the battery
        current_soc: The current state of charge (between 0 and 100)
        target_soc: The target state of charge (between 0 and 100, defaults to 80)
        efficiency: The efficiency of the charging process (between 0 and 1, defaults to 0.9)

    Returns:
        The estimated time to charge in h
    """

    one_percent_capacity = battery_capacity / 100
    charging_rates = zip(
        charging_curve[current_soc:target_soc],
        charging_curve[current_soc + 1 : target_soc + 1],
    )

    return (
        sum(
            2 * one_percent_capacity / (current_rate + next_rate)
            for (current_rate, next_rate) in charging_rates
        )
        / efficiency
    )


def get_charging_windows(
    battery_capacity: float,
    charging_curve: list[float],
    soc_curve: pd.Series,
    energy_mix: pd.DataFrame,
    min_soc: int = 20,
    max_soc: int = 80,
) -> list[tuple[datetime, datetime, float]]:
    """
    Get the possible charging windows given an energy mix and soc curve.

    Args:
        battery_capacity: The capacity of the battery
        charging_curve: The charging curve of the battery
        soc_curve: The current state of charge (between 0 and 100) at every hour
        energy_mix: The predicted energy mix at every hour

    Returns:
        A list containing the possible charging windows sorted by cost (asc). Each charging window
        is a tuple of the form (start, end, cost), where `cost = emissions * charged_soc`.
    """

    def to_absolute_emissions(col: pd.Series):
        if col.name not in ["datetime", "Sum"]:
            return col * CO2_COEFFICIENTS[col.name]
        return col

    get_time_to_fully_charge = functools.partial(
        get_time_to_charge,
        battery_capacity=battery_capacity,
        charging_curve=charging_curve,
    )

    df = energy_mix.apply(to_absolute_emissions, axis=0)
    df["soc"] = soc_curve
    df = df[(df["soc"] >= min_soc) & (df["soc"] < max_soc)]
    emission_cols = [col for col in df.columns if col not in ["datetime", "soc"]]
    df["Sum"] = df[emission_cols].sum(axis=1)
    df["finish_time"] = df.apply(
        lambda row: row["datetime"]
        + timedelta(hours=get_time_to_fully_charge(current_soc=row["soc"])),
        axis=1,
    )
    df["charging_emissions"] = df.apply(
        lambda row: df[
            (df["datetime"] >= row["datetime"])
            & (df["datetime"] <= (row["finish_time"]).ceil("H"))
        ]["Sum"].sum(),
        axis=1,
    )
    df["cost"] = df.apply(
        lambda row: row["charging_emissions"] * (max_soc - row["soc"]), axis=1
    )

    charging_windows = [
        (start.to_pydatetime(), end.round("T").to_pydatetime(), cost)
        for (start, end, cost) in df[["datetime", "finish_time", "cost"]].itertuples(
            index=False, name=None
        )
    ]
    return sorted(charging_windows, key=lambda t: t[2])
