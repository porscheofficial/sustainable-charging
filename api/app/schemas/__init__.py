from pydantic import field_validator
from enum import Enum
import datetime
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
    end_time: str | None = None # Optional field in case of single commutes

    @field_validator('start_time', 'end_time')
    def validate_time_format(cls, v):
        if v is None:
         return v  # Return None without validation

        if not re.match(r"^\d{2}:\d{2}(:\d{2})?$", v):
            raise ValueError("Time must be in HH:MM or HH:MM:SS format")
        return v # has to be string because firestore doesn't support datetime.time

class TrafficLevel(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"

class CommuteEntity(CamelModel):
    name: str
    is_round_trip: bool
    usage: list[UsageEntry]
    approx_distance_km: float
    approx_duration_minutes: float
    traffic: TrafficLevel
