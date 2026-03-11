"""
Phase 7 Analytics - Backend API Tests
======================================
Tests for:
- Analytics Engine (hunting trips)
- Tracking Engine V1 (events, funnels, heatmaps, engagement)

Test coverage:
- Module info endpoints
- CRUD operations
- Data aggregation
- Funnel analysis
- Heatmap generation
- Engagement metrics
"""
import pytest
import requests
import os
from datetime import datetime

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')


class TestAnalyticsEngineModuleInfo:
    """Analytics Engine module info tests"""
    
    def test_analytics_module_info(self):
        """GET /api/v1/analytics/ - Returns module info"""
        response = requests.get(f"{BASE_URL}/api/v1/analytics/")
        assert response.status_code == 200
        
        data = response.json()
        assert data["module"] == "analytics_engine"
        assert data["version"] == "1.0.0"
        assert "endpoints" in data
        assert len(data["endpoints"]) >= 10


class TestAnalyticsDashboard:
    """Analytics dashboard endpoint tests"""
    
    def test_dashboard_returns_valid_structure(self):
        """GET /api/v1/analytics/dashboard - Returns dashboard data"""
        response = requests.get(f"{BASE_URL}/api/v1/analytics/dashboard")
        assert response.status_code == 200
        
        data = response.json()
        assert "overview" in data
        assert "species_breakdown" in data
        assert "weather_analysis" in data
        assert "optimal_times" in data
        assert "monthly_trends" in data
        
    def test_dashboard_overview_structure(self):
        """Dashboard overview has correct fields"""
        response = requests.get(f"{BASE_URL}/api/v1/analytics/dashboard")
        assert response.status_code == 200
        
        overview = response.json()["overview"]
        assert "total_trips" in overview
        assert "success_rate" in overview
        assert "total_hours" in overview
        assert "total_observations" in overview
        
    def test_dashboard_with_time_range_filter(self):
        """Dashboard accepts time_range parameter"""
        for time_range in ["week", "month", "season", "year", "all"]:
            response = requests.get(f"{BASE_URL}/api/v1/analytics/dashboard?time_range={time_range}")
            assert response.status_code == 200


class TestTrackingEngineModuleInfo:
    """Tracking Engine module info tests"""
    
    def test_tracking_module_info(self):
        """GET /api/v1/tracking-engine/ - Returns module info"""
        response = requests.get(f"{BASE_URL}/api/v1/tracking-engine/")
        assert response.status_code == 200
        
        data = response.json()
        assert data["module"] == "tracking_engine"
        assert data["version"] == "1.0.0"
        assert "features" in data
        assert "endpoints" in data
        
        # Verify features
        features = data["features"]
        assert "Event tracking (clicks, page views, scrolls)" in features
        assert "Conversion funnels" in features
        assert "Heatmaps" in features
        assert "Session analysis" in features
        assert "Engagement metrics" in features


class TestTrackingEngineEvents:
    """Tracking Engine events tests"""
    
    def test_get_events_returns_list(self):
        """GET /api/v1/tracking-engine/events - Returns events list"""
        response = requests.get(f"{BASE_URL}/api/v1/tracking-engine/events")
        assert response.status_code == 200
        
        data = response.json()
        assert isinstance(data, list)
        
    def test_get_events_with_filters(self):
        """GET /api/v1/tracking-engine/events - Accepts filter parameters"""
        response = requests.get(f"{BASE_URL}/api/v1/tracking-engine/events?event_type=page_view&limit=10")
        assert response.status_code == 200
        
        data = response.json()
        assert isinstance(data, list)
        assert len(data) <= 10
        
    def test_track_single_event(self):
        """POST /api/v1/tracking-engine/events - Tracks a single event"""
        event_data = {
            "session_id": "test-session-pytest",
            "event_type": "page_view",
            "event_name": "test_page_view",
            "page_url": "https://huntiq.com/test",
            "page_title": "Test Page"
        }
        
        response = requests.post(
            f"{BASE_URL}/api/v1/tracking-engine/events",
            json=event_data
        )
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] == True
        assert "event_id" in data
        
    def test_batch_track_events(self):
        """POST /api/v1/tracking-engine/events/batch - Tracks multiple events"""
        events = [
            {
                "session_id": "test-batch-session",
                "event_type": "page_view",
                "event_name": "batch_test_1",
                "page_url": "https://huntiq.com/batch1"
            },
            {
                "session_id": "test-batch-session",
                "event_type": "click",
                "event_name": "batch_test_2",
                "page_url": "https://huntiq.com/batch2"
            }
        ]
        
        response = requests.post(
            f"{BASE_URL}/api/v1/tracking-engine/events/batch",
            json=events
        )
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] == True
        assert data["events_tracked"] == 2


class TestTrackingEngineFunnels:
    """Tracking Engine funnels tests"""
    
    @pytest.fixture
    def created_funnel_id(self):
        """Create a test funnel and return its ID"""
        funnel_data = {
            "name": "Pytest Test Funnel",
            "description": "Funnel created by pytest",
            "steps": [
                {"step_number": 1, "event_name": "page_view__", "event_type": "page_view"},
                {"step_number": 2, "event_name": "click__map", "event_type": "click"}
            ]
        }
        
        response = requests.post(
            f"{BASE_URL}/api/v1/tracking-engine/funnels",
            json=funnel_data
        )
        
        if response.status_code == 200:
            funnel_id = response.json()["funnel"]["id"]
            yield funnel_id
            # Cleanup
            requests.delete(f"{BASE_URL}/api/v1/tracking-engine/funnels/{funnel_id}")
        else:
            yield None
    
    def test_create_funnel(self):
        """POST /api/v1/tracking-engine/funnels - Creates a funnel"""
        funnel_data = {
            "name": "Test Create Funnel",
            "description": "Test funnel creation",
            "steps": [
                {"step_number": 1, "event_name": "test_step_1", "event_type": "page_view"},
                {"step_number": 2, "event_name": "test_step_2", "event_type": "click"}
            ]
        }
        
        response = requests.post(
            f"{BASE_URL}/api/v1/tracking-engine/funnels",
            json=funnel_data
        )
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] == True
        assert "funnel" in data
        assert data["funnel"]["name"] == "Test Create Funnel"
        
        # Cleanup
        funnel_id = data["funnel"]["id"]
        requests.delete(f"{BASE_URL}/api/v1/tracking-engine/funnels/{funnel_id}")
        
    def test_list_funnels(self):
        """GET /api/v1/tracking-engine/funnels - Lists all funnels"""
        response = requests.get(f"{BASE_URL}/api/v1/tracking-engine/funnels")
        assert response.status_code == 200
        
        data = response.json()
        assert isinstance(data, list)
        
    def test_get_funnel_by_id(self, created_funnel_id):
        """GET /api/v1/tracking-engine/funnels/{id} - Gets funnel by ID"""
        if not created_funnel_id:
            pytest.skip("Funnel creation failed")
            
        response = requests.get(f"{BASE_URL}/api/v1/tracking-engine/funnels/{created_funnel_id}")
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] == True
        assert "funnel" in data
        
    def test_analyze_funnel(self, created_funnel_id):
        """GET /api/v1/tracking-engine/funnels/{id}/analyze - Analyzes funnel"""
        if not created_funnel_id:
            pytest.skip("Funnel creation failed")
            
        response = requests.get(f"{BASE_URL}/api/v1/tracking-engine/funnels/{created_funnel_id}/analyze")
        assert response.status_code == 200
        
        data = response.json()
        assert "funnel_id" in data
        assert "funnel_name" in data
        assert "total_started" in data
        assert "total_completed" in data
        assert "conversion_rate" in data
        assert "steps_analysis" in data
        
    def test_delete_funnel(self):
        """DELETE /api/v1/tracking-engine/funnels/{id} - Deletes funnel"""
        # Create a funnel to delete
        funnel_data = {
            "name": "Funnel To Delete",
            "steps": [{"step_number": 1, "event_name": "delete_test", "event_type": "page_view"}]
        }
        
        create_response = requests.post(
            f"{BASE_URL}/api/v1/tracking-engine/funnels",
            json=funnel_data
        )
        assert create_response.status_code == 200
        funnel_id = create_response.json()["funnel"]["id"]
        
        # Delete the funnel
        delete_response = requests.delete(f"{BASE_URL}/api/v1/tracking-engine/funnels/{funnel_id}")
        assert delete_response.status_code == 200
        
        data = delete_response.json()
        assert data["success"] == True
        
        # Verify deletion
        get_response = requests.get(f"{BASE_URL}/api/v1/tracking-engine/funnels/{funnel_id}")
        assert get_response.status_code == 404


class TestTrackingEngineHeatmap:
    """Tracking Engine heatmap tests"""
    
    def test_get_heatmap_data(self):
        """GET /api/v1/tracking-engine/heatmap - Returns heatmap data"""
        response = requests.get(
            f"{BASE_URL}/api/v1/tracking-engine/heatmap?page_url=https://huntiq.com/"
        )
        assert response.status_code == 200
        
        data = response.json()
        assert "page_url" in data
        assert "viewport_width" in data
        assert "viewport_height" in data
        assert "total_clicks" in data
        assert "points" in data
        assert isinstance(data["points"], list)
        
    def test_heatmap_with_custom_viewport(self):
        """Heatmap accepts custom viewport parameters"""
        response = requests.get(
            f"{BASE_URL}/api/v1/tracking-engine/heatmap?page_url=https://huntiq.com/&viewport_width=1280&viewport_height=720"
        )
        assert response.status_code == 200
        
        data = response.json()
        assert data["viewport_width"] == 1280
        assert data["viewport_height"] == 720


class TestTrackingEngineEngagement:
    """Tracking Engine engagement metrics tests"""
    
    def test_get_engagement_metrics(self):
        """GET /api/v1/tracking-engine/engagement - Returns engagement metrics"""
        response = requests.get(f"{BASE_URL}/api/v1/tracking-engine/engagement")
        assert response.status_code == 200
        
        data = response.json()
        assert "total_sessions" in data
        assert "total_page_views" in data
        assert "total_events" in data
        assert "unique_users" in data
        assert "bounce_rate" in data
        assert "pages_per_session" in data
        assert "top_pages" in data
        assert "top_events" in data
        assert "device_breakdown" in data
        assert "country_breakdown" in data
        
    def test_engagement_metrics_with_days_filter(self):
        """Engagement metrics accepts days parameter"""
        response = requests.get(f"{BASE_URL}/api/v1/tracking-engine/engagement?days=7")
        assert response.status_code == 200
        
        data = response.json()
        assert "time_range_start" in data
        assert "time_range_end" in data


class TestTrackingEngineSeed:
    """Tracking Engine seed data tests"""
    
    def test_seed_demo_data(self):
        """POST /api/v1/tracking-engine/seed - Generates demo data"""
        response = requests.post(f"{BASE_URL}/api/v1/tracking-engine/seed")
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] == True
        assert "count" in data
        assert data["count"] > 0


class TestAnalyticsEngineTrips:
    """Analytics Engine trips CRUD tests"""
    
    def test_get_trips_list(self):
        """GET /api/v1/analytics/trips - Returns trips list"""
        response = requests.get(f"{BASE_URL}/api/v1/analytics/trips")
        assert response.status_code == 200
        
        data = response.json()
        assert isinstance(data, list)
        
    def test_create_trip(self):
        """POST /api/v1/analytics/trips - Creates a hunting trip"""
        trip_data = {
            "date": datetime.now().isoformat(),
            "species": "moose",
            "location_lat": 46.8139,
            "location_lng": -71.2082,
            "duration_hours": 4.5,
            "success": True,
            "observations": 3,
            "weather_condition": "clear",
            "notes": "Test trip from pytest"
        }
        
        response = requests.post(
            f"{BASE_URL}/api/v1/analytics/trips",
            json=trip_data
        )
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] == True
        assert "trip" in data
        
    def test_analytics_seed_demo_data(self):
        """POST /api/v1/analytics/seed - Generates demo hunting trips"""
        response = requests.post(f"{BASE_URL}/api/v1/analytics/seed")
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] == True
        assert "count" in data


class TestAnalyticsEngineStatistics:
    """Analytics Engine statistics endpoints tests"""
    
    def test_get_overview_stats(self):
        """GET /api/v1/analytics/overview - Returns overview statistics"""
        response = requests.get(f"{BASE_URL}/api/v1/analytics/overview")
        assert response.status_code == 200
        
        data = response.json()
        assert "total_trips" in data
        assert "success_rate" in data
        assert "total_hours" in data
        assert "total_observations" in data
        
    def test_get_species_breakdown(self):
        """GET /api/v1/analytics/species - Returns species breakdown"""
        response = requests.get(f"{BASE_URL}/api/v1/analytics/species")
        assert response.status_code == 200
        
        data = response.json()
        assert isinstance(data, list)
        
    def test_get_weather_analysis(self):
        """GET /api/v1/analytics/weather - Returns weather analysis"""
        response = requests.get(f"{BASE_URL}/api/v1/analytics/weather")
        assert response.status_code == 200
        
        data = response.json()
        assert isinstance(data, list)
        
    def test_get_optimal_times(self):
        """GET /api/v1/analytics/optimal-times - Returns optimal hunting times"""
        response = requests.get(f"{BASE_URL}/api/v1/analytics/optimal-times")
        assert response.status_code == 200
        
        data = response.json()
        assert isinstance(data, list)
        
    def test_get_monthly_trends(self):
        """GET /api/v1/analytics/trends - Returns monthly trends"""
        response = requests.get(f"{BASE_URL}/api/v1/analytics/trends")
        assert response.status_code == 200
        
        data = response.json()
        assert isinstance(data, list)


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
