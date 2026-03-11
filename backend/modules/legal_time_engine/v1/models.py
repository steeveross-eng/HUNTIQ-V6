"""Legal Time Engine Models

Pydantic models for legal hunting time calculations.

Version: 1.0.0
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Literal
from datetime import datetime, date, time


class LocationInput(BaseModel):
    """Location input for sun calculations"""
    latitude: float = Field(default=46.8139, ge=-90, le=90, description="Latitude")
    longitude: float = Field(default=-71.2080, ge=-180, le=180, description="Longitude")
    timezone: str = Field(default="America/Toronto", description="Timezone name")


class SunTimes(BaseModel):
    """Sunrise and sunset times"""
    date: date
    sunrise: time
    sunset: time
    dawn: time  # Civil dawn (before sunrise)
    dusk: time  # Civil dusk (after sunset)
    day_length_minutes: int
    

class LegalHuntingWindow(BaseModel):
    """Legal hunting window based on regulations"""
    date: date
    start_time: time = Field(description="30 minutes before sunrise")
    end_time: time = Field(description="30 minutes after sunset")
    duration_minutes: int
    sunrise: time
    sunset: time
    is_currently_legal: bool = False
    current_status: Literal["before_legal", "legal", "after_legal"] = "before_legal"
    next_legal_start: Optional[datetime] = None


class HuntingTimeSlot(BaseModel):
    """A recommended hunting time slot"""
    period_name: str
    start_time: time
    end_time: time
    score: int = Field(ge=0, le=100, description="Quality score 0-100")
    is_legal: bool = True
    light_condition: Literal["dark", "dawn", "daylight", "dusk", "twilight"] = "daylight"
    recommendation: str = ""


class DailyHuntingSchedule(BaseModel):
    """Complete daily hunting schedule with legal windows"""
    date: date
    location: LocationInput
    legal_window: LegalHuntingWindow
    sun_times: SunTimes
    recommended_slots: List[HuntingTimeSlot] = []
    best_slot: Optional[HuntingTimeSlot] = None
    moon_phase: Optional[str] = None


class MultiDayForecast(BaseModel):
    """Multi-day hunting time forecast"""
    location: LocationInput
    start_date: date
    days: int
    schedules: List[DailyHuntingSchedule] = []
