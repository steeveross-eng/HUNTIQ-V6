"""
Test Legal Time Engine and Predictive Engine APIs
Phase 8 - Natural Light & Legality Window Feature

Tests:
- Legal Time Engine: /api/v1/legal-time/*
- Predictive Engine: /api/v1/predictive/*
"""

import pytest
import requests
import os
from datetime import date

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Default Quebec City coordinates
DEFAULT_LAT = 46.8139
DEFAULT_LNG = -71.2080


class TestLegalTimeEngineInfo:
    """Test Legal Time Engine module info endpoint"""
    
    def test_legal_time_info(self):
        """GET /api/v1/legal-time/ - Module info"""
        response = requests.get(f"{BASE_URL}/api/v1/legal-time/")
        assert response.status_code == 200
        
        data = response.json()
        assert data["module"] == "legal_time_engine"
        assert data["version"] == "1.0.0"
        assert "regulations" in data
        assert data["regulations"]["jurisdiction"] == "Québec, Canada"
        assert "default_location" in data
        assert data["default_location"]["latitude"] == 46.8139


class TestLegalTimeEngineSunTimes:
    """Test sun times calculation endpoint"""
    
    def test_sun_times_default(self):
        """GET /api/v1/legal-time/sun-times - Default location"""
        response = requests.get(
            f"{BASE_URL}/api/v1/legal-time/sun-times",
            params={"lat": DEFAULT_LAT, "lng": DEFAULT_LNG}
        )
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] is True
        assert "sun_times" in data
        assert "sunrise" in data["sun_times"]
        assert "sunset" in data["sun_times"]
        assert "dawn" in data["sun_times"]
        assert "dusk" in data["sun_times"]
        assert "day_length_hours" in data["sun_times"]
        
        # Validate time format (HH:MM)
        assert len(data["sun_times"]["sunrise"]) == 5
        assert ":" in data["sun_times"]["sunrise"]
    
    def test_sun_times_with_date(self):
        """GET /api/v1/legal-time/sun-times - With specific date"""
        response = requests.get(
            f"{BASE_URL}/api/v1/legal-time/sun-times",
            params={"date": "2026-06-21", "lat": DEFAULT_LAT, "lng": DEFAULT_LNG}
        )
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] is True
        assert data["date"] == "2026-06-21"
    
    def test_sun_times_invalid_date(self):
        """GET /api/v1/legal-time/sun-times - Invalid date format"""
        response = requests.get(
            f"{BASE_URL}/api/v1/legal-time/sun-times",
            params={"date": "invalid-date", "lat": DEFAULT_LAT, "lng": DEFAULT_LNG}
        )
        assert response.status_code == 400


class TestLegalTimeEngineLegalWindow:
    """Test legal hunting window calculation endpoint"""
    
    def test_legal_window_default(self):
        """GET /api/v1/legal-time/legal-window - Default location"""
        response = requests.get(
            f"{BASE_URL}/api/v1/legal-time/legal-window",
            params={"lat": DEFAULT_LAT, "lng": DEFAULT_LNG}
        )
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] is True
        assert "legal_window" in data
        assert "start_time" in data["legal_window"]
        assert "end_time" in data["legal_window"]
        assert "duration_hours" in data["legal_window"]
        assert "sunrise" in data["legal_window"]
        assert "sunset" in data["legal_window"]
        
        # Validate status
        assert "status" in data
        assert "is_currently_legal" in data["status"]
        assert "current_status" in data["status"]
        
        # Validate regulation text
        assert "regulation" in data
    
    def test_legal_window_30min_rule(self):
        """Verify 30-minute before/after rule"""
        response = requests.get(
            f"{BASE_URL}/api/v1/legal-time/legal-window",
            params={"lat": DEFAULT_LAT, "lng": DEFAULT_LNG}
        )
        data = response.json()
        
        # Parse times
        start_time = data["legal_window"]["start_time"]
        sunrise = data["legal_window"]["sunrise"]
        end_time = data["legal_window"]["end_time"]
        sunset = data["legal_window"]["sunset"]
        
        # Convert to minutes for comparison
        def time_to_minutes(t):
            h, m = map(int, t.split(":"))
            return h * 60 + m
        
        start_mins = time_to_minutes(start_time)
        sunrise_mins = time_to_minutes(sunrise)
        end_mins = time_to_minutes(end_time)
        sunset_mins = time_to_minutes(sunset)
        
        # Legal start should be 30 min before sunrise
        assert sunrise_mins - start_mins == 30
        # Legal end should be 30 min after sunset
        assert end_mins - sunset_mins == 30


class TestLegalTimeEngineCheck:
    """Test current legal status check endpoint"""
    
    def test_check_legal_now(self):
        """GET /api/v1/legal-time/check - Current status"""
        response = requests.get(
            f"{BASE_URL}/api/v1/legal-time/check",
            params={"lat": DEFAULT_LAT, "lng": DEFAULT_LNG}
        )
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] is True
        assert "current_time" in data
        assert "is_legal" in data
        assert isinstance(data["is_legal"], bool)
        assert "message" in data
        assert "legal_window" in data
        assert "start" in data["legal_window"]
        assert "end" in data["legal_window"]


class TestLegalTimeEngineRecommendedSlots:
    """Test recommended hunting slots endpoint"""
    
    def test_recommended_slots(self):
        """GET /api/v1/legal-time/recommended-slots - Get slots"""
        response = requests.get(
            f"{BASE_URL}/api/v1/legal-time/recommended-slots",
            params={"lat": DEFAULT_LAT, "lng": DEFAULT_LNG}
        )
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] is True
        assert "slots" in data
        assert len(data["slots"]) > 0
        
        # Validate slot structure
        slot = data["slots"][0]
        assert "period" in slot
        assert "start_time" in slot
        assert "end_time" in slot
        assert "score" in slot
        assert "light_condition" in slot
        assert "recommendation" in slot
        assert "is_legal" in slot
        
        # All slots should be legal
        for slot in data["slots"]:
            assert slot["is_legal"] is True
        
        # Validate best_slot
        assert "best_slot" in data
        assert data["best_slot"]["score"] >= 90  # Dawn should be highest


class TestLegalTimeEngineSchedule:
    """Test daily schedule endpoint"""
    
    def test_daily_schedule(self):
        """GET /api/v1/legal-time/schedule - Daily schedule"""
        response = requests.get(
            f"{BASE_URL}/api/v1/legal-time/schedule",
            params={"lat": DEFAULT_LAT, "lng": DEFAULT_LNG}
        )
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] is True
        assert "schedule" in data
        
        schedule = data["schedule"]
        assert "date" in schedule
        assert "location" in schedule
        assert "sun_times" in schedule
        assert "legal_window" in schedule
        assert "recommended_slots" in schedule
        assert "best_period" in schedule


class TestLegalTimeEngineForecast:
    """Test multi-day forecast endpoint"""
    
    def test_forecast_7_days(self):
        """GET /api/v1/legal-time/forecast - 7 day forecast"""
        response = requests.get(
            f"{BASE_URL}/api/v1/legal-time/forecast",
            params={"days": 7, "lat": DEFAULT_LAT, "lng": DEFAULT_LNG}
        )
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] is True
        assert "forecast" in data
        
        forecast = data["forecast"]
        assert forecast["days"] == 7
        assert "daily_schedules" in forecast
        assert len(forecast["daily_schedules"]) == 7
        
        # Validate each day
        for day in forecast["daily_schedules"]:
            assert "date" in day
            assert "legal_start" in day
            assert "legal_end" in day
            assert "sunrise" in day
            assert "sunset" in day
    
    def test_forecast_max_days(self):
        """GET /api/v1/legal-time/forecast - Max 14 days"""
        response = requests.get(
            f"{BASE_URL}/api/v1/legal-time/forecast",
            params={"days": 14, "lat": DEFAULT_LAT, "lng": DEFAULT_LNG}
        )
        assert response.status_code == 200
        
        data = response.json()
        assert len(data["forecast"]["daily_schedules"]) == 14


class TestPredictiveEngineInfo:
    """Test Predictive Engine module info endpoint"""
    
    def test_predictive_info(self):
        """GET /api/v1/predictive/ - Module info"""
        response = requests.get(f"{BASE_URL}/api/v1/predictive/")
        assert response.status_code == 200
        
        data = response.json()
        assert data["module"] == "predictive_engine"
        assert data["version"] == "1.0.0"
        assert "supported_species" in data
        assert "deer" in data["supported_species"]


class TestPredictiveEngineSuccess:
    """Test hunting success prediction endpoint"""
    
    def test_predict_success_deer(self):
        """GET /api/v1/predictive/success - Deer prediction"""
        response = requests.get(
            f"{BASE_URL}/api/v1/predictive/success",
            params={"species": "deer", "lat": DEFAULT_LAT, "lng": DEFAULT_LNG}
        )
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] is True
        assert data["species"] == "deer"
        assert "prediction" in data
        
        prediction = data["prediction"]
        assert "success_probability" in prediction
        assert 0 <= prediction["success_probability"] <= 100
        assert "confidence" in prediction
        assert "factors" in prediction
        assert "optimal_times" in prediction
        assert "recommendation" in prediction
        
        # Validate factors
        assert len(prediction["factors"]) > 0
        for factor in prediction["factors"]:
            assert "name" in factor
            assert "impact" in factor
            assert "score" in factor
            assert "description" in factor
        
        # Validate optimal times respect legal window
        for time in prediction["optimal_times"]:
            assert "is_legal" in time
            assert time["is_legal"] is True
    
    def test_predict_success_moose(self):
        """GET /api/v1/predictive/success - Moose prediction"""
        response = requests.get(
            f"{BASE_URL}/api/v1/predictive/success",
            params={"species": "moose", "lat": DEFAULT_LAT, "lng": DEFAULT_LNG}
        )
        assert response.status_code == 200
        
        data = response.json()
        assert data["species"] == "moose"


class TestPredictiveEngineActivity:
    """Test current activity level endpoint"""
    
    def test_activity_level(self):
        """GET /api/v1/predictive/activity - Current activity"""
        response = requests.get(
            f"{BASE_URL}/api/v1/predictive/activity",
            params={"species": "deer", "lat": DEFAULT_LAT, "lng": DEFAULT_LNG}
        )
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] is True
        assert data["species"] == "deer"
        assert "activity" in data
        
        activity = data["activity"]
        assert "level" in activity
        assert activity["level"] in ["very_low", "low", "moderate", "high", "very_high"]
        assert "score" in activity
        assert 0 <= activity["score"] <= 100
        assert "peak_times" in activity


class TestPredictiveEngineFactors:
    """Test success factors endpoint"""
    
    def test_success_factors(self):
        """GET /api/v1/predictive/factors - Success factors"""
        response = requests.get(
            f"{BASE_URL}/api/v1/predictive/factors",
            params={"species": "deer"}
        )
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] is True
        assert "overall_score" in data
        assert "factors" in data
        assert len(data["factors"]) >= 5


class TestPredictiveEngineTimeline:
    """Test hourly activity timeline endpoint"""
    
    def test_activity_timeline(self):
        """GET /api/v1/predictive/timeline - Hourly timeline"""
        response = requests.get(
            f"{BASE_URL}/api/v1/predictive/timeline",
            params={"species": "deer", "lat": DEFAULT_LAT, "lng": DEFAULT_LNG}
        )
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] is True
        assert "timeline" in data
        assert len(data["timeline"]) == 24  # 24 hours
        
        # Validate timeline structure
        for hour_data in data["timeline"]:
            assert "hour" in hour_data
            assert "time" in hour_data
            assert "activity_level" in hour_data
            assert "is_legal" in hour_data
            assert "light_condition" in hour_data
        
        # Validate legal window reference
        assert "legal_window" in data
        assert "peak_hours" in data


class TestLegalTimeIntegration:
    """Test integration between Legal Time and Predictive engines"""
    
    def test_optimal_times_within_legal_window(self):
        """Verify optimal times are within legal hunting window"""
        # Get legal window
        legal_response = requests.get(
            f"{BASE_URL}/api/v1/legal-time/legal-window",
            params={"lat": DEFAULT_LAT, "lng": DEFAULT_LNG}
        )
        legal_data = legal_response.json()
        
        # Get prediction
        pred_response = requests.get(
            f"{BASE_URL}/api/v1/predictive/success",
            params={"species": "deer", "lat": DEFAULT_LAT, "lng": DEFAULT_LNG}
        )
        pred_data = pred_response.json()
        
        # All optimal times should be marked as legal
        for time in pred_data["prediction"]["optimal_times"]:
            assert time["is_legal"] is True, f"Optimal time {time['time']} should be legal"
    
    def test_timeline_legal_hours_match(self):
        """Verify timeline legal hours match legal window"""
        # Get legal window
        legal_response = requests.get(
            f"{BASE_URL}/api/v1/legal-time/legal-window",
            params={"lat": DEFAULT_LAT, "lng": DEFAULT_LNG}
        )
        legal_data = legal_response.json()
        
        # Get timeline
        timeline_response = requests.get(
            f"{BASE_URL}/api/v1/predictive/timeline",
            params={"species": "deer", "lat": DEFAULT_LAT, "lng": DEFAULT_LNG}
        )
        timeline_data = timeline_response.json()
        
        # Parse legal window times (use ceiling for start, floor for end)
        def time_to_hour_ceil(t):
            h, m = map(int, t.split(":"))
            return h + 1 if m > 0 else h  # Round up if minutes > 0
        
        def time_to_hour_floor(t):
            return int(t.split(":")[0])
        
        # Legal start at 06:28 means hour 7 is first fully legal hour
        legal_start_hour = time_to_hour_ceil(legal_data["legal_window"]["start_time"])
        # Legal end at 17:30 means hour 17 is last fully legal hour
        legal_end_hour = time_to_hour_floor(legal_data["legal_window"]["end_time"])
        
        # Verify timeline legal flags for fully legal hours
        for hour_data in timeline_data["timeline"]:
            hour = hour_data["hour"]
            is_legal = hour_data["is_legal"]
            
            # Hours fully within legal window should be marked legal
            if legal_start_hour <= hour <= legal_end_hour:
                assert is_legal is True, f"Hour {hour} should be legal"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
