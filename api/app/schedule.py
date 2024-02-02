from datetime import datetime
import pandas as pd
from fastapi import APIRouter, Query
from firestore import db
from schemas import ChargingWindow, User
from api.app.core.charging_scheduler import (
    get_soc_curve_from_commutes,
    get_charging_windows,
)


router = APIRouter(prefix="/schedule", tags=["schedule"])


@router.get("/", response_model=list[ChargingWindow])
async def get_schedule(
    user_id: int = Query(None, description="User ID"),
    initial_soc: float = Query(
        100, description="Initial state of charge (between 0 and 100)"
    ),
) -> list[ChargingWindow]:
    """
    Get schedule for list of commute_ids (as app is not user specific yet)
    """

    user = get_user_by_id(user_id)
    car = get_car_model_by_id(user.car_model_id)

    # Get all the commutes for the given user
    commutes = db.collection("commutes").where("user_id", "==", user_id).stream()

    # Get the energy mix TODO use @raphaels endpoint to query real energy mix
    file_path = "./predictions/mock_predictions.csv"
    energy_mix = pd.read_csv(file_path, delimiter=";")

    # calculate charging windows
    soc_curve = get_soc_curve_from_commutes(
        commutes, datetime.datetime.now(), initial_soc, car
    )
    charging_windows = get_charging_windows(
        car_model=car,
        soc_curve=soc_curve,
        energy_mix=energy_mix,
    )

    return [
        ChargingWindow(
            start_time=start_time.isoformat(),
            end_time=end_time.isoformat(),
            emissions=emissions,
        )
        for (start_time, end_time, emissions) in charging_windows
    ]


def get_user_by_id(user_id: int) -> User:
    """Get a user given their ID"""
    user_collection = db.collection("users")
    user_snapshot = user_collection.document(str(user_id))
    if not user_snapshot.exists:
        raise ValueError(f"User with ID {user_id} does not exist.")

    return User(**user_snapshot.to_dict())


def get_car_model_by_id(car_model_id: int) -> User:
    """Get a car model given its ID"""
    car_model_collection = db.collection("car_models")
    car_model_snapshot = car_model_collection.document(str(car_model_id))
    if not car_model_snapshot.exists:
        raise ValueError(f"Car Model with ID {car_model_id} does not exist.")

    return User(**car_model_snapshot.to_dict())
