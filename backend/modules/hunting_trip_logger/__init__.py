"""
Hunting Trip Logger Module
Real data logging for hunting trips, waypoint visits, and observations
"""

from .v1.router import router
from .v1.service import HuntingTripLoggerService

__all__ = ['router', 'HuntingTripLoggerService']
__version__ = '1.0.0'
