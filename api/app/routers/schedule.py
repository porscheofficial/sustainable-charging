import pathlib
import sys

base_path = pathlib.Path(__file__).parents[3]
sys.path.append(str(base_path))

from datetime import datetime, timedelta
from fastapi import APIRouter, Query

from mongodb import MongoDBClient
from schemas import CarModel, ChargingWindow, CommuteEntity, User
from core.charging_scheduler import (
    get_soc_curve_from_commutes,
    get_charging_windows,
)
from model.inference.inference_helper import InferenceHelper
from model.scripts.fetch_live_data import fetch

db = MongoDBClient()
router = APIRouter(prefix="/schedule", tags=["schedule"])


@router.get("/", response_model=list[ChargingWindow])
async def get_schedule(
    user_id: str = Query(None, description="User ID"),
    initial_soc: float = Query(
        100, description="Initial state of charge (between 0 and 100)"
    ),
    min_charging_duration: int = Query(
        5, description="Minimum charging duration in minutes"
    ),
    max_charging_power: int = Query(
        30, description="Maximum charging power (defaults to 30 kW)"
    ),
) -> list[ChargingWindow]:
    """Get the charging schedule for a specific user.

    Args
    ----
        user_id: The ID of the user
        initial_soc: The initial state of charge of the user's car (defaults to 100)
        min_charging_duration: The minimum charging duration (defaults to 5 min)
        max_charging_power: The maximum charging power available (defaults to 30 kW)

    Returns
    -------
        A list of charging windows sorted by cost (asc)

    """
    user = get_user_by_name(user_id)
    if user is None:
        return []

    car = get_car_model_by_name(user.car_model_id)

    # Get all the commutes for the given user
    commutes = [
        CommuteEntity(**doc) for doc in db.find_commutes_by_user_id(user_id=user_id)
    ]

    m = InferenceHelper(str(base_path / "model_results" / "lstm"))

    data_req = m.get_data_request_info(
        7 * 24
    )  # Data requirements for 7 days ahead prediction
    smard_data, weather_data = fetch(data_req)
    prediction = m.predict(smard_data, weather_data, 7 * 24)
    energy_mix = prediction.pd_dataframe()
    energy_mix = energy_mix.reset_index()

    # calculate charging windows
    soc_curve = get_soc_curve_from_commutes(
        commutes,
        datetime(
            datetime.now().year, datetime.now().month, datetime.now().day, 0, 0, 0
        ),
        initial_soc,
        car,
    )
    charging_windows = get_charging_windows(
        car_model=car,
        soc_curve=soc_curve,
        energy_mix=energy_mix,
        min_charging_duration=timedelta(minutes=min_charging_duration),
        max_charging_power=max_charging_power,
    )

    return [
        ChargingWindow(
            start_time=start_time.isoformat(),
            end_time=end_time.isoformat(),
            emissions=round(emissions / 1000, 2),
        )
        for (start_time, end_time, emissions) in charging_windows
    ]


def get_user_by_name(user: str) -> User:
    """Get a user given their ID."""
    user = db.find_user_by_name(user)
    if user is None:
        return None

    return User(**user)


def get_car_model_by_name(car_model: str) -> CarModel:
    """Get a car model given its ID."""
    car = db.find_car_model_by_name(car_model)
    if car is None:
        raise ValueError(f"Car Model with ID {car_model} does not exist.")

    return CarModel(**car)
