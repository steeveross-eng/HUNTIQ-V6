"""
Hunting Trip Logger v1
Real data logging for hunting trips, waypoint visits, and observations
"""

from .router import router
from .service import HuntingTripLoggerService
from .models import (
    TripCreate, TripStart, TripEnd, HuntingTrip, TripStatus,
    WaypointVisitCreate, WaypointVisit,
    ObservationCreate, Observation, ObservationType,
    TripStatistics, WaypointStatistics, WeatherCondition
)

__all__ = [
    'router',
    'HuntingTripLoggerService',
    'TripCreate', 'TripStart', 'TripEnd', 'HuntingTrip', 'TripStatus',
    'WaypointVisitCreate', 'WaypointVisit',
    'ObservationCreate', 'Observation', 'ObservationType',
    'TripStatistics', 'WaypointStatistics', 'WeatherCondition'
]
