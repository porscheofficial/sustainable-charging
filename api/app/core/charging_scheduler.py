from datetime import datetime, time, timedelta
from math import floor
import functools
import pandas as pd
from schemas import CommuteEntity, CarModel
from model import config

WEEK_DAYS = {"MON": 0, "TUE": 1, "WED": 2, "THU": 3, "FRI": 4, "SAT": 5, "SUN": 6}


def get_soc_curve_from_commutes(
    commutes: list[CommuteEntity],
    start: datetime,
    initial_soc: float,
    car_model: CarModel,
) -> pd.Series:
    """
    Get a prediction of the state of charge over the next week given a list of commutes.

    Args:
        commutes: A list of commutes during the next seven days
        start: The time and date when the prediction should start
        initial_soc: The initial state of charge
        car_model: The car model of which the SOC should be predicted

    Returns:
        A pandas.Series with the hourly predicted SOC over the next seven days.
    """
    seven_day_hourly_index = pd.date_range(
        start=start.replace(minute=0, second=0, microsecond=0), periods=7 * 24, freq="H"
    )
    soc_curve = pd.Series(
        [initial_soc] * len(seven_day_hourly_index),
        dtype="float64",
        name="soc",
        index=seven_day_hourly_index,
    )

    if len(commutes) == 0:
        return soc_curve

    trips = []
    for commute in commutes:
        for trip in commute.usage:
            start_time = time.fromisoformat(trip.start_time)

            # we should store trip.day as integers instead of strings
            trip_start = (
                start + timedelta(days=((WEEK_DAYS[trip.day] - start.weekday()) % 7))
            ).replace(
                hour=start_time.hour, minute=start_time.minute, second=0, microsecond=0
            )

            if trip.end_time:
                end_time = time.fromisoformat(trip.end_time)
                trip_end = (
                    start
                    + timedelta(days=((WEEK_DAYS[trip.day] - start.weekday()) % 7))
                ).replace(
                    hour=end_time.hour, minute=end_time.minute, second=0, microsecond=0
                )
            else:
                trip_end = trip_start + timedelta(
                    minutes=commute.approx_distance_minutes
                )

            trip_soc_change = (
                car_model.consumption_per_kilometer * commute.approx_distance_km
            ) / (
                10 * car_model.battery_capacity
            )  # (Wh/km * km * 100) / (1000 * Wh) = %

            trips.append((trip_start, trip_end, trip_soc_change))

    trips.sort(key=lambda t: t[1])

    current_soc = initial_soc
    last_updated_hour = None
    last_trip_end = soc_curve.index[0]
    for trip_start, trip_end, soc_change in trips:
        for i in soc_curve.loc[
            (soc_curve.index > last_trip_end) & (soc_curve.index <= trip_start)
        ].index:
            soc_curve.at[i] = current_soc
        last_trip_end = trip_end
        mask = (soc_curve.index > trip_start) & (
            soc_curve.index < trip_end + timedelta(hours=1)
        )
        affected_rows = soc_curve.loc[mask]
        partial_soc_change = soc_change / len(affected_rows)
        for i in affected_rows.index:
            current_soc -= partial_soc_change
            soc_curve.at[i] = max(current_soc, 0)
            last_updated_hour = i
            if current_soc <= 0:
                break

    for i in soc_curve.loc[soc_curve.index > last_updated_hour].index:
        soc_curve.at[i] = current_soc

    return soc_curve


def get_time_to_charge(
    car_model: CarModel,
    current_soc: float,
    max_charging_power: int,
    target_soc: int = 80,
    efficiency: float = 0.9,
) -> float:
    """
    Get the estimated time to charge from the current state of charge (SOC) to a target SOC.

    Args:
        car_model: The car model that is being charged
        current_soc: The current state of charge (between 0 and 100)
        target_soc: The target state of charge (between 0 and 100, defaults to 80)
        efficiency: The efficiency of the charging process (between 0 and 1, defaults to 0.9)

    Returns:
        The estimated time to charge in h
    """

    current_soc = floor(
        current_soc
    )  # floor current_soc to get conservative estimate in case of non-integer soc
    one_percent_capacity = car_model.battery_capacity / 100
    charging_rates = zip(
        car_model.charging_curve[current_soc:target_soc],
        car_model.charging_curve[current_soc + 1 : target_soc + 1],
    )

    return (
        sum(
            2
            * one_percent_capacity
            / min(current_rate + next_rate, 2 * max_charging_power)
            for (current_rate, next_rate) in charging_rates
        )
        / efficiency
    )


def get_charging_windows(
    car_model: CarModel,
    soc_curve: pd.Series,
    energy_mix: pd.DataFrame,
    min_charging_duration: timedelta,
    max_charging_power: int,
    min_soc: int = 20,
    max_soc: int = 80,
) -> list[tuple[datetime, datetime, float]]:
    """
    Get the possible charging windows given an energy mix and soc curve.

    Args:
        car_model: The car model that is being charged
        soc_curve: The current state of charge (between 0 and 100) at every hour
        energy_mix: The predicted energy mix at every hour
        min_charging_duration: A lower bound for the charging duration
        min_soc: A lower bound for the SOC where charging is considered
        max_soc: An upper bound for the SOC where charging is considered

    Returns:
        A list containing the possible charging windows sorted by cost (asc). Each charging window
        is a tuple of the form (start, end, cost), where `cost` is the gCO2 emitted during charging.
    """

    def to_relative_emissions(col: pd.Series, sum_col: pd.Series):
        if col.name not in ["timestamp", "Sum", "soc"]:
            return col / sum_col * config.EMISSION_FACTORS[col.name]
        return col

    get_time_to_fully_charge = functools.partial(
        get_time_to_charge, car_model=car_model, max_charging_power=max_charging_power
    )

    df = energy_mix.merge(right=soc_curve, left_on="timestamp", right_index=True)

    df = df[df["soc"] <= max_soc]
    if not (above_min_soc := df[df["soc"] >= min_soc]).empty:  # pylint: disable=C0103
        df = above_min_soc

    emission_cols = [
        col for col in df.columns if col not in ["timestamp", "soc", "Sum"]
    ]

    df["Sum"] = df[emission_cols].sum(axis=1)
    create_relative_emissions = functools.partial(
        to_relative_emissions, sum_col=df["Sum"]
    )
    df = df.apply(create_relative_emissions, axis=0)
    df = df.assign(  # pylint: disable=C0103
        finish_time=df.apply(
            lambda row: row["timestamp"]
            + timedelta(hours=get_time_to_fully_charge(current_soc=row["soc"])),
            axis=1,
        )
    )
    df["TotalEmissions"] = df[emission_cols].sum(axis=1)

    df["charging_emissions"] = df.apply(
        lambda row: df[
            (df["timestamp"] >= row["timestamp"])
            & (df["timestamp"] <= (row["finish_time"]).ceil("H"))
        ]["TotalEmissions"].mean(),
        axis=1,
    )

    df["cost"] = df.apply(
        lambda row: row["charging_emissions"]
        * (max_soc - row["soc"])
        / 100
        * car_model.battery_capacity,
        axis=1,
    )

    charging_windows = [
        (
            start_time,
            end_time,
            cost,
        )
        for (start, end, cost) in df[["timestamp", "finish_time", "cost"]].itertuples(
            index=False, name=None
        )
        if (end_time := end.round("min").to_pydatetime())
        - (start_time := start.to_pydatetime())
        >= min_charging_duration
    ]

    return sorted(charging_windows, key=lambda t: t[2])
