from pydantic import field_validator
from enum import Enum
from fastapi_camelcase import CamelModel
import re


class DayOfWeek(str, Enum):
    SUN = "SUN"
    MON = "MON"
    TUE = "TUE"
    WED = "WED"
    THU = "THU"
    FRI = "FRI"
    SAT = "SAT"


class UsageEntry(CamelModel):
    day: DayOfWeek
    start_time: str
    end_time: str | None = None  # Optional field in case of single commutes

    @field_validator("start_time", "end_time")
    def validate_time_format(cls, v):
        if v is None:
            return v  # Return None without validation

        if not re.match(r"^\d{2}:\d{2}(:\d{2})?$", v):
            raise ValueError("Time must be in HH:MM or HH:MM:SS format")
        return v  # has to be string because firestore doesn't support datetime.time


class TrafficLevel(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"


class CommuteEntity(CamelModel):
    user_id: str
    name: str
    is_round_trip: bool
    usage: list[UsageEntry]
    approx_distance_km: float
    approx_duration_minutes: float
    traffic: TrafficLevel


class ChargingWindow(CamelModel):
    start_time: str
    end_time: str
    emissions: float


class CarModel(CamelModel):
    name: str
    battery_capacity: float
    charging_curve: list[float]
    consumption_per_kilometer: float

    @field_validator("charging_curve")
    def validate_charging_curve(cls, v):
        if len(v) != 101:
            raise ValueError(
                f"The charging curve must have exactly 101 values, {len(v)} given."
            )
        return v


class User(CamelModel):
    name: str
    car_model_id: str
