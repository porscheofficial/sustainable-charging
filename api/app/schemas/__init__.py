import re
from enum import Enum
from typing import Any, Dict

from pydantic import field_validator
from fastapi_camelcase import CamelModel


class DayOfWeek(str, Enum):
    """Enum for storing Days of the Week."""

    SUN = "SUN"
    MON = "MON"
    TUE = "TUE"
    WED = "WED"
    THU = "THU"
    FRI = "FRI"
    SAT = "SAT"


class UsageEntry(CamelModel):
    """Usage Entry Model."""

    day: DayOfWeek
    start_time: str
    end_time: str | None = None  # Optional field in case of single commutes

    @field_validator("start_time")
    @classmethod
    def validate_start_time_format(cls, v):  # pylint: disable=C0103
        """Validate time format."""
        if v is None:
            raise ValueError("Start Date can not be None")

        if not re.match(r"^\d{2}:\d{2}(:\d{2})?$", v):
            raise ValueError("Time must be in HH:MM or HH:MM:SS format")
        return v

    @field_validator("end_time")
    @classmethod
    def validate_end_time_format(cls, v):  # pylint: disable=C0103
        """Validate time format."""
        if not re.match(r"^\d{2}:\d{2}(:\d{2})?$", v):
            raise ValueError("Time must be in HH:MM or HH:MM:SS format")
        return v

    def to_dict(self) -> Dict[str, Any]:
        """
        Custom method to convert a UsageEntry instance into a dictionary,
        ensuring all Enum types are converted to their string representation
        and handling None values gracefully.
        """
        return {
            "day": self.day.value,  # Convert Enum to its string value
            "startTime": self.start_time,
            "endTime": self.end_time,  # This will be None if not set, no need for special handling
        }


class TrafficLevel(str, Enum):
    """Enum for storing Traffic Levels."""

    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"


class CommuteEntity(CamelModel):
    """Commute Model."""

    user_id: str
    name: str
    is_round_trip: bool
    usage: list[UsageEntry]
    approx_distance_km: float
    approx_duration_minutes: float
    traffic: TrafficLevel

    def to_dict(self) -> Dict[str, Any]:
        """
        Custom method to convert a CommuteEntity instance into a dictionary,
        ensuring all Enum types are converted to their string representation.
        """
        return {
            "userId": self.user_id,
            "name": self.name,
            "isRoundTrip": self.is_round_trip,
            "usage": [entry.to_dict() for entry in self.usage],
            "approxDistanceKm": self.approx_distance_km,
            "approxDurationMinutes": self.approx_duration_minutes,
            "traffic": self.traffic.value,  # Convert Enum to its string value
        }


class ChargingWindow(CamelModel):
    """Charging Window Model."""

    start_time: str
    end_time: str
    emissions: float


class CarModel(CamelModel):
    """Car Model."""

    name: str
    battery_capacity: float
    charging_curve: list[float]
    consumption_per_kilometer: float

    @field_validator("charging_curve")
    @classmethod
    def validate_charging_curve(cls, v: list[float]):  # pylint: disable=C0103
        """Validate charging curve."""
        if len(v) != 101:
            raise ValueError(
                f"The charging curve must have exactly 101 values, {len(v)} given."
            )
        return v

    def to_dict(self) -> Dict[str, Any]:
        """
        Custom method to convert a CarModel instance into a dictionary,
        ensuring all Enum types are converted to their string representation.
        """
        return {
            "name": self.name,
            "battery_capacity": self.battery_capacity,
            "charging_curve": self.charging_curve,
            "consumption_per_kilometer": self.consumption_per_kilometer,
        }


class User(CamelModel):
    """User Model."""

    name: str
    car_model_id: str

    def to_dict(self) -> Dict[str, Any]:
        """
        Custom method to convert a User instance into a dictionary,
        ensuring all Enum types are converted to their string representation.
        """
        return {"name": self.name, "car_model_id": self.car_model_id}
