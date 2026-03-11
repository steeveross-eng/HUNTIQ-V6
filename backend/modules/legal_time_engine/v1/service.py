"""Legal Time Engine Service

Business logic for calculating legal hunting times based on sunrise/sunset.
Uses the Astral library for accurate astronomical calculations.

Quebec Hunting Regulations:
- Legal hunting starts 30 minutes BEFORE sunrise
- Legal hunting ends 30 minutes AFTER sunset

Version: 1.0.0
"""

from datetime import datetime, date, time, timedelta
from typing import List, Optional, Tuple
from astral import LocationInfo
from astral.sun import sun
from zoneinfo import ZoneInfo

from .models import (
    LocationInput, SunTimes, LegalHuntingWindow, 
    HuntingTimeSlot, DailyHuntingSchedule, MultiDayForecast
)


class LegalTimeService:
    """Service for calculating legal hunting times"""
    
    # Default location: Quebec City, QC, Canada
    DEFAULT_LOCATION = LocationInput(
        latitude=46.8139,
        longitude=-71.2080,
        timezone="America/Toronto"
    )
    
    # Quebec hunting regulation: time before/after sunrise/sunset
    LEGAL_OFFSET_MINUTES = 30
    
    def __init__(self):
        self.location = self.DEFAULT_LOCATION
    
    def get_sun_times(self, target_date: date, location: Optional[LocationInput] = None) -> SunTimes:
        """
        Calculate sunrise, sunset, dawn, and dusk times for a given date and location.
        
        Args:
            target_date: The date to calculate for
            location: Optional location override
            
        Returns:
            SunTimes object with all calculated times
        """
        loc = location or self.DEFAULT_LOCATION
        
        # Create Astral location
        loc_info = LocationInfo(
            name="Custom",
            region="Custom",
            timezone=loc.timezone,
            latitude=loc.latitude,
            longitude=loc.longitude
        )
        
        # Get timezone
        tz = ZoneInfo(loc.timezone)
        
        # Calculate sun times
        s = sun(loc_info.observer, date=target_date, tzinfo=tz)
        
        # Extract times
        sunrise_dt = s["sunrise"]
        sunset_dt = s["sunset"]
        dawn_dt = s["dawn"]  # Civil dawn
        dusk_dt = s["dusk"]  # Civil dusk
        
        # Calculate day length
        day_length = (sunset_dt - sunrise_dt).total_seconds() / 60
        
        return SunTimes(
            date=target_date,
            sunrise=sunrise_dt.time(),
            sunset=sunset_dt.time(),
            dawn=dawn_dt.time(),
            dusk=dusk_dt.time(),
            day_length_minutes=int(day_length)
        )
    
    def get_legal_hunting_window(
        self, 
        target_date: date, 
        location: Optional[LocationInput] = None
    ) -> LegalHuntingWindow:
        """
        Calculate the legal hunting window for a given date.
        
        Quebec regulations:
        - Start: 30 minutes before sunrise
        - End: 30 minutes after sunset
        
        Args:
            target_date: The date to calculate for
            location: Optional location override
            
        Returns:
            LegalHuntingWindow with start/end times
        """
        loc = location or self.DEFAULT_LOCATION
        sun_times = self.get_sun_times(target_date, loc)
        
        # Get timezone
        tz = ZoneInfo(loc.timezone)
        
        # Create datetime objects for calculations
        sunrise_dt = datetime.combine(target_date, sun_times.sunrise, tzinfo=tz)
        sunset_dt = datetime.combine(target_date, sun_times.sunset, tzinfo=tz)
        
        # Calculate legal window
        legal_start_dt = sunrise_dt - timedelta(minutes=self.LEGAL_OFFSET_MINUTES)
        legal_end_dt = sunset_dt + timedelta(minutes=self.LEGAL_OFFSET_MINUTES)
        
        # Calculate duration
        duration = (legal_end_dt - legal_start_dt).total_seconds() / 60
        
        # Determine current status
        now = datetime.now(tz)
        is_today = target_date == now.date()
        
        if is_today:
            current_time = now.time()
            is_legal = legal_start_dt.time() <= current_time <= legal_end_dt.time()
            
            if current_time < legal_start_dt.time():
                status = "before_legal"
                next_start = legal_start_dt
            elif current_time > legal_end_dt.time():
                status = "after_legal"
                # Next legal start is tomorrow
                tomorrow = target_date + timedelta(days=1)
                tomorrow_window = self.get_legal_hunting_window(tomorrow, loc)
                next_start = datetime.combine(
                    tomorrow, 
                    tomorrow_window.start_time, 
                    tzinfo=tz
                )
            else:
                status = "legal"
                next_start = None
        else:
            is_legal = False
            status = "before_legal" if target_date > now.date() else "after_legal"
            next_start = legal_start_dt if target_date > now.date() else None
        
        return LegalHuntingWindow(
            date=target_date,
            start_time=legal_start_dt.time(),
            end_time=legal_end_dt.time(),
            duration_minutes=int(duration),
            sunrise=sun_times.sunrise,
            sunset=sun_times.sunset,
            is_currently_legal=is_legal,
            current_status=status,
            next_legal_start=next_start
        )
    
    def get_recommended_hunting_slots(
        self, 
        target_date: date,
        location: Optional[LocationInput] = None
    ) -> List[HuntingTimeSlot]:
        """
        Get recommended hunting time slots within the legal window.
        
        Best times are typically:
        1. Dawn (30 min before to 2 hours after sunrise) - Score: 90-95
        2. Dusk (2 hours before to 30 min after sunset) - Score: 85-90
        3. Mid-morning (2-4 hours after sunrise) - Score: 50-60
        4. Early afternoon (2-4 hours before sunset) - Score: 40-50
        
        Returns:
            List of HuntingTimeSlot sorted by score
        """
        loc = location or self.DEFAULT_LOCATION
        legal_window = self.get_legal_hunting_window(target_date, loc)
        sun_times = self.get_sun_times(target_date, loc)
        
        tz = ZoneInfo(loc.timezone)
        
        # Create datetime objects
        sunrise_dt = datetime.combine(target_date, sun_times.sunrise, tzinfo=tz)
        sunset_dt = datetime.combine(target_date, sun_times.sunset, tzinfo=tz)
        legal_start = datetime.combine(target_date, legal_window.start_time, tzinfo=tz)
        legal_end = datetime.combine(target_date, legal_window.end_time, tzinfo=tz)
        
        slots = []
        
        # 1. Dawn slot (best) - Legal start to 2 hours after sunrise
        dawn_end = sunrise_dt + timedelta(hours=2)
        slots.append(HuntingTimeSlot(
            period_name="Aube",
            start_time=legal_start.time(),
            end_time=min(dawn_end, legal_end).time(),
            score=95,
            is_legal=True,
            light_condition="dawn",
            recommendation="Période optimale - Les cervidés sont très actifs à l'aube"
        ))
        
        # 2. Morning slot - 2 to 4 hours after sunrise
        morning_start = sunrise_dt + timedelta(hours=2)
        morning_end = sunrise_dt + timedelta(hours=4)
        if morning_start < legal_end:
            slots.append(HuntingTimeSlot(
                period_name="Matinée",
                start_time=morning_start.time(),
                end_time=min(morning_end, legal_end).time(),
                score=55,
                is_legal=True,
                light_condition="daylight",
                recommendation="Activité modérée - Bonne pour la chasse à l'affût"
            ))
        
        # 3. Midday slot - middle of the day
        midday_start = sunrise_dt + timedelta(hours=4)
        midday_end = sunset_dt - timedelta(hours=4)
        if midday_start < midday_end:
            slots.append(HuntingTimeSlot(
                period_name="Mi-journée",
                start_time=midday_start.time(),
                end_time=midday_end.time(),
                score=35,
                is_legal=True,
                light_condition="daylight",
                recommendation="Activité faible - Les animaux se reposent généralement"
            ))
        
        # 4. Afternoon slot - 4 to 2 hours before sunset
        afternoon_start = sunset_dt - timedelta(hours=4)
        afternoon_end = sunset_dt - timedelta(hours=2)
        if afternoon_start > sunrise_dt:
            slots.append(HuntingTimeSlot(
                period_name="Après-midi",
                start_time=max(afternoon_start, legal_start).time(),
                end_time=afternoon_end.time(),
                score=50,
                is_legal=True,
                light_condition="daylight",
                recommendation="Activité en augmentation - Les animaux commencent à bouger"
            ))
        
        # 5. Dusk slot (excellent) - 2 hours before to legal end
        dusk_start = sunset_dt - timedelta(hours=2)
        slots.append(HuntingTimeSlot(
            period_name="Crépuscule",
            start_time=max(dusk_start, legal_start).time(),
            end_time=legal_end.time(),
            score=90,
            is_legal=True,
            light_condition="dusk",
            recommendation="Période excellente - Forte activité avant la nuit"
        ))
        
        # Sort by score descending
        slots.sort(key=lambda x: x.score, reverse=True)
        
        return slots
    
    def get_daily_schedule(
        self,
        target_date: date,
        location: Optional[LocationInput] = None
    ) -> DailyHuntingSchedule:
        """
        Get a complete daily hunting schedule with all information.
        """
        loc = location or self.DEFAULT_LOCATION
        
        sun_times = self.get_sun_times(target_date, loc)
        legal_window = self.get_legal_hunting_window(target_date, loc)
        recommended_slots = self.get_recommended_hunting_slots(target_date, loc)
        
        return DailyHuntingSchedule(
            date=target_date,
            location=loc,
            legal_window=legal_window,
            sun_times=sun_times,
            recommended_slots=recommended_slots,
            best_slot=recommended_slots[0] if recommended_slots else None
        )
    
    def get_multi_day_forecast(
        self,
        start_date: date,
        days: int = 7,
        location: Optional[LocationInput] = None
    ) -> MultiDayForecast:
        """
        Get a multi-day hunting time forecast.
        
        Args:
            start_date: First date of the forecast
            days: Number of days to forecast (default: 7)
            location: Optional location override
            
        Returns:
            MultiDayForecast with schedules for each day
        """
        loc = location or self.DEFAULT_LOCATION
        
        schedules = []
        for i in range(days):
            day = start_date + timedelta(days=i)
            schedule = self.get_daily_schedule(day, loc)
            schedules.append(schedule)
        
        return MultiDayForecast(
            location=loc,
            start_date=start_date,
            days=days,
            schedules=schedules
        )
    
    def is_time_legal(
        self,
        check_datetime: datetime,
        location: Optional[LocationInput] = None
    ) -> Tuple[bool, str]:
        """
        Check if a specific datetime is within legal hunting hours.
        
        Args:
            check_datetime: The datetime to check
            location: Optional location override
            
        Returns:
            Tuple of (is_legal, message)
        """
        loc = location or self.DEFAULT_LOCATION
        target_date = check_datetime.date()
        
        legal_window = self.get_legal_hunting_window(target_date, loc)
        
        check_time = check_datetime.time()
        
        if check_time < legal_window.start_time:
            minutes_until = self._time_diff_minutes(check_time, legal_window.start_time)
            return False, f"Hors période légale. La chasse débute dans {minutes_until} minutes."
        elif check_time > legal_window.end_time:
            return False, "Hors période légale. La chasse est terminée pour aujourd'hui."
        else:
            minutes_remaining = self._time_diff_minutes(check_time, legal_window.end_time)
            return True, f"Période légale. {minutes_remaining} minutes restantes."
    
    def _time_diff_minutes(self, t1: time, t2: time) -> int:
        """Calculate minutes between two times"""
        today = date.today()
        dt1 = datetime.combine(today, t1)
        dt2 = datetime.combine(today, t2)
        diff = (dt2 - dt1).total_seconds() / 60
        return int(abs(diff))
