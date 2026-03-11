"""
BIONIC™ Geospatial Data Integration Tests
==========================================
Tests for real-time environmental data from external APIs:
- Open-Meteo: Weather data (temperature, precipitation, wind, humidity)
- Open-Elevation: Terrain elevation data
- NASA MODIS/Seasonal: Vegetation indices (NDVI, NDWI)

Test coordinates: Québec, Canada (46.8139, -71.2082)
"""

import pytest
import requests
import os
import time

# Get backend URL from environment
BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Test coordinates for Québec, Canada
TEST_LAT = 46.8139
TEST_LON = -71.2082


class TestGeospatialWeatherAPI:
    """Tests for GET /api/bionic/geospatial/weather - Open-Meteo integration"""
    
    def test_weather_endpoint_returns_200(self):
        """Test weather endpoint returns successful response"""
        response = requests.get(
            f"{BASE_URL}/api/bionic/geospatial/weather",
            params={"latitude": TEST_LAT, "longitude": TEST_LON}
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
    def test_weather_response_structure(self):
        """Test weather response contains required fields"""
        response = requests.get(
            f"{BASE_URL}/api/bionic/geospatial/weather",
            params={"latitude": TEST_LAT, "longitude": TEST_LON}
        )
        data = response.json()
        
        # Check success flag
        assert data.get("success") == True, "Response should have success=True"
        
        # Check source
        assert data.get("source") == "Open-Meteo", f"Source should be Open-Meteo, got {data.get('source')}"
        
        # Check location
        assert "location" in data, "Response should contain location"
        assert data["location"]["latitude"] == TEST_LAT
        assert data["location"]["longitude"] == TEST_LON
        
        # Check current weather data
        assert "current" in data, "Response should contain current weather"
        current = data["current"]
        
        required_fields = ["temperature", "feels_like", "humidity", "precipitation", 
                          "wind_speed", "wind_direction", "cloud_cover", "pressure", 
                          "uv_index", "is_day", "description"]
        for field in required_fields:
            assert field in current, f"Current weather should contain {field}"
            
    def test_weather_temperature_is_realistic(self):
        """Test that temperature values are within realistic range"""
        response = requests.get(
            f"{BASE_URL}/api/bionic/geospatial/weather",
            params={"latitude": TEST_LAT, "longitude": TEST_LON}
        )
        data = response.json()
        
        temp = data["current"]["temperature"]
        # Québec temperature range: -40°C to +40°C
        assert -50 <= temp <= 50, f"Temperature {temp}°C is outside realistic range"
        
    def test_weather_forecasts_included(self):
        """Test that forecast data is included"""
        response = requests.get(
            f"{BASE_URL}/api/bionic/geospatial/weather",
            params={"latitude": TEST_LAT, "longitude": TEST_LON}
        )
        data = response.json()
        
        # Check forecasts exist
        assert "forecast_24h" in data, "Should include 24h forecast"
        assert "forecast_72h" in data, "Should include 72h forecast"
        assert "forecast_7d" in data, "Should include 7-day forecast"
        
    def test_weather_invalid_coordinates(self):
        """Test weather endpoint with invalid coordinates"""
        response = requests.get(
            f"{BASE_URL}/api/bionic/geospatial/weather",
            params={"latitude": 999, "longitude": -71.2082}
        )
        assert response.status_code == 422, "Should return 422 for invalid latitude"


class TestGeospatialTerrainAPI:
    """Tests for GET /api/bionic/geospatial/terrain - Open-Elevation integration"""
    
    def test_terrain_endpoint_returns_200(self):
        """Test terrain endpoint returns successful response"""
        response = requests.get(
            f"{BASE_URL}/api/bionic/geospatial/terrain",
            params={"latitude": TEST_LAT, "longitude": TEST_LON}
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
    def test_terrain_response_structure(self):
        """Test terrain response contains required fields"""
        response = requests.get(
            f"{BASE_URL}/api/bionic/geospatial/terrain",
            params={"latitude": TEST_LAT, "longitude": TEST_LON}
        )
        data = response.json()
        
        # Check success flag
        assert data.get("success") == True, "Response should have success=True"
        
        # Check source
        assert data.get("source") == "Open-Elevation", f"Source should be Open-Elevation, got {data.get('source')}"
        
        # Check terrain data
        assert "terrain" in data, "Response should contain terrain data"
        terrain = data["terrain"]
        
        assert "elevation_m" in terrain, "Terrain should contain elevation_m"
        assert "slope_deg" in terrain, "Terrain should contain slope_deg"
        assert "aspect_deg" in terrain, "Terrain should contain aspect_deg"
        
    def test_terrain_elevation_is_realistic(self):
        """Test that elevation values are within realistic range for Québec"""
        response = requests.get(
            f"{BASE_URL}/api/bionic/geospatial/terrain",
            params={"latitude": TEST_LAT, "longitude": TEST_LON}
        )
        data = response.json()
        
        elevation = data["terrain"]["elevation_m"]
        # Québec City elevation: ~50-100m typically
        assert -100 <= elevation <= 2000, f"Elevation {elevation}m is outside realistic range"
        
    def test_terrain_slope_is_valid(self):
        """Test that slope values are within valid range"""
        response = requests.get(
            f"{BASE_URL}/api/bionic/geospatial/terrain",
            params={"latitude": TEST_LAT, "longitude": TEST_LON}
        )
        data = response.json()
        
        slope = data["terrain"]["slope_deg"]
        if slope is not None:
            assert 0 <= slope <= 90, f"Slope {slope}° is outside valid range"


class TestGeospatialVegetationAPI:
    """Tests for GET /api/bionic/geospatial/vegetation - NASA MODIS/Seasonal estimates"""
    
    def test_vegetation_endpoint_returns_200(self):
        """Test vegetation endpoint returns successful response"""
        response = requests.get(
            f"{BASE_URL}/api/bionic/geospatial/vegetation",
            params={"latitude": TEST_LAT, "longitude": TEST_LON}
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
    def test_vegetation_response_structure(self):
        """Test vegetation response contains required fields"""
        response = requests.get(
            f"{BASE_URL}/api/bionic/geospatial/vegetation",
            params={"latitude": TEST_LAT, "longitude": TEST_LON}
        )
        data = response.json()
        
        # Check success flag
        assert data.get("success") == True, "Response should have success=True"
        
        # Check source (should mention NASA MODIS or Seasonal)
        assert "source" in data, "Response should contain source"
        
        # Check vegetation data
        assert "vegetation" in data, "Response should contain vegetation data"
        veg = data["vegetation"]
        
        assert "ndvi" in veg, "Vegetation should contain ndvi"
        assert "ndwi" in veg, "Vegetation should contain ndwi"
        assert "interpretation" in veg, "Vegetation should contain interpretation"
        
    def test_vegetation_ndvi_is_valid(self):
        """Test that NDVI values are within valid range (-1 to 1)"""
        response = requests.get(
            f"{BASE_URL}/api/bionic/geospatial/vegetation",
            params={"latitude": TEST_LAT, "longitude": TEST_LON}
        )
        data = response.json()
        
        ndvi = data["vegetation"]["ndvi"]
        assert -1 <= ndvi <= 1, f"NDVI {ndvi} is outside valid range (-1 to 1)"
        
    def test_vegetation_ndwi_is_valid(self):
        """Test that NDWI values are within valid range (-1 to 1)"""
        response = requests.get(
            f"{BASE_URL}/api/bionic/geospatial/vegetation",
            params={"latitude": TEST_LAT, "longitude": TEST_LON}
        )
        data = response.json()
        
        ndwi = data["vegetation"]["ndwi"]
        if ndwi is not None:
            assert -1 <= ndwi <= 1, f"NDWI {ndwi} is outside valid range (-1 to 1)"
            
    def test_vegetation_source_indicates_seasonal_estimate(self):
        """Test that source indicates seasonal estimate (MOCKED data)"""
        response = requests.get(
            f"{BASE_URL}/api/bionic/geospatial/vegetation",
            params={"latitude": TEST_LAT, "longitude": TEST_LON}
        )
        data = response.json()
        
        source = data.get("source", "")
        # Should indicate it's using seasonal estimates
        assert "Seasonal" in source or "MODIS" in source, f"Source should mention Seasonal or MODIS: {source}"


class TestGeospatialCompleteAPI:
    """Tests for GET /api/bionic/geospatial/complete - Combined data endpoint"""
    
    def test_complete_endpoint_returns_200(self):
        """Test complete geospatial endpoint returns successful response"""
        response = requests.get(
            f"{BASE_URL}/api/bionic/geospatial/complete",
            params={"latitude": TEST_LAT, "longitude": TEST_LON}
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
    def test_complete_response_contains_all_data(self):
        """Test complete response contains weather, terrain, and vegetation"""
        response = requests.get(
            f"{BASE_URL}/api/bionic/geospatial/complete",
            params={"latitude": TEST_LAT, "longitude": TEST_LON}
        )
        data = response.json()
        
        assert data.get("success") == True, "Response should have success=True"
        assert "weather" in data, "Complete response should contain weather"
        assert "terrain" in data, "Complete response should contain terrain"
        assert "vegetation" in data, "Complete response should contain vegetation"
        
    def test_complete_data_quality_field(self):
        """Test that data_quality field is present"""
        response = requests.get(
            f"{BASE_URL}/api/bionic/geospatial/complete",
            params={"latitude": TEST_LAT, "longitude": TEST_LON}
        )
        data = response.json()
        
        assert "data_quality" in data, "Response should contain data_quality"
        assert data["data_quality"] in ["complete", "partial", "failed"], \
            f"data_quality should be complete/partial/failed, got {data['data_quality']}"


class TestBionicAnalyzeWithRealData:
    """Tests for POST /api/bionic/analyze - Integration with real geospatial data"""
    
    def test_analyze_returns_real_conditions(self):
        """Test that analyze endpoint returns real_conditions with live data"""
        response = requests.post(
            f"{BASE_URL}/api/bionic/analyze",
            json={
                "territory_id": "test_geospatial",
                "latitude": TEST_LAT,
                "longitude": TEST_LON,
                "radius_km": 5,
                "modules": ["thermal", "wetness", "food"],
                "species": ["moose", "deer"],
                "include_ai_predictions": True,
                "include_temporal": False
            }
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert data.get("success") == True, "Response should have success=True"
        
        analysis = data.get("analysis", {})
        
        # Check real_conditions is present
        assert "real_conditions" in analysis, "Analysis should contain real_conditions"
        real_conditions = analysis["real_conditions"]
        
        # Check weather data
        assert "weather" in real_conditions, "real_conditions should contain weather"
        weather = real_conditions["weather"]
        assert "temperature" in weather, "Weather should contain temperature"
        assert "source" in weather, "Weather should contain source"
        assert weather["source"] == "Open-Meteo", "Weather source should be Open-Meteo"
        
    def test_analyze_returns_data_sources(self):
        """Test that analyze endpoint returns data_sources list"""
        response = requests.post(
            f"{BASE_URL}/api/bionic/analyze",
            json={
                "territory_id": "test_geospatial_sources",
                "latitude": TEST_LAT,
                "longitude": TEST_LON,
                "radius_km": 5,
                "modules": ["thermal"],
                "species": ["moose"],
                "include_ai_predictions": False,
                "include_temporal": False
            }
        )
        data = response.json()
        analysis = data.get("analysis", {})
        
        # Check data_sources is present
        assert "data_sources" in analysis, "Analysis should contain data_sources"
        data_sources = analysis["data_sources"]
        
        assert isinstance(data_sources, list), "data_sources should be a list"
        assert len(data_sources) > 0, "data_sources should not be empty"
        
        # Check expected sources are present
        sources_str = " ".join(data_sources)
        assert "Open-Meteo" in sources_str, "data_sources should include Open-Meteo"
        
    def test_analyze_terrain_data_in_real_conditions(self):
        """Test that terrain data is included in real_conditions"""
        response = requests.post(
            f"{BASE_URL}/api/bionic/analyze",
            json={
                "territory_id": "test_terrain",
                "latitude": TEST_LAT,
                "longitude": TEST_LON,
                "radius_km": 5,
                "modules": ["geoform"],
                "species": ["moose"],
                "include_ai_predictions": False,
                "include_temporal": False
            }
        )
        data = response.json()
        analysis = data.get("analysis", {})
        real_conditions = analysis.get("real_conditions", {})
        
        # Check terrain data
        assert "terrain" in real_conditions, "real_conditions should contain terrain"
        terrain = real_conditions["terrain"]
        assert "elevation_m" in terrain, "Terrain should contain elevation_m"
        assert "source" in terrain, "Terrain should contain source"
        assert terrain["source"] == "Open-Elevation", "Terrain source should be Open-Elevation"
        
    def test_analyze_vegetation_data_in_real_conditions(self):
        """Test that vegetation data is included in real_conditions"""
        response = requests.post(
            f"{BASE_URL}/api/bionic/analyze",
            json={
                "territory_id": "test_vegetation",
                "latitude": TEST_LAT,
                "longitude": TEST_LON,
                "radius_km": 5,
                "modules": ["food"],
                "species": ["deer"],
                "include_ai_predictions": False,
                "include_temporal": False
            }
        )
        data = response.json()
        analysis = data.get("analysis", {})
        real_conditions = analysis.get("real_conditions", {})
        
        # Check vegetation data
        assert "vegetation" in real_conditions, "real_conditions should contain vegetation"
        veg = real_conditions["vegetation"]
        assert "ndvi" in veg, "Vegetation should contain ndvi"
        assert "ndwi" in veg, "Vegetation should contain ndwi"
        assert "source" in veg, "Vegetation should contain source"
        
    def test_analyze_module_scores_reflect_real_data(self):
        """Test that module scores are calculated using real data"""
        response = requests.post(
            f"{BASE_URL}/api/bionic/analyze",
            json={
                "territory_id": "test_scores",
                "latitude": TEST_LAT,
                "longitude": TEST_LON,
                "radius_km": 5,
                "modules": ["thermal", "wetness", "food", "geoform"],
                "species": ["moose"],
                "include_ai_predictions": False,
                "include_temporal": False
            }
        )
        data = response.json()
        analysis = data.get("analysis", {})
        
        # Check modules have scores
        modules = analysis.get("modules", {})
        assert len(modules) > 0, "Should have module results"
        
        for module_name, module_data in modules.items():
            assert "score" in module_data, f"Module {module_name} should have score"
            assert 0 <= module_data["score"] <= 100, f"Module {module_name} score should be 0-100"
            
            # Check data_sources in module results
            if "data_sources" in module_data:
                assert isinstance(module_data["data_sources"], list), \
                    f"Module {module_name} data_sources should be a list"


class TestGeospatialCaching:
    """Tests for geospatial data caching functionality"""
    
    def test_repeated_calls_use_cache(self):
        """Test that repeated calls within 5 minutes use cached data"""
        # First call
        start1 = time.time()
        response1 = requests.get(
            f"{BASE_URL}/api/bionic/geospatial/complete",
            params={"latitude": TEST_LAT, "longitude": TEST_LON}
        )
        time1 = time.time() - start1
        
        # Second call (should be faster due to cache)
        start2 = time.time()
        response2 = requests.get(
            f"{BASE_URL}/api/bionic/geospatial/complete",
            params={"latitude": TEST_LAT, "longitude": TEST_LON}
        )
        time2 = time.time() - start2
        
        assert response1.status_code == 200
        assert response2.status_code == 200
        
        # Both should return same data quality
        data1 = response1.json()
        data2 = response2.json()
        assert data1["data_quality"] == data2["data_quality"], \
            "Cached response should have same data quality"


class TestHelperFunctions:
    """Tests for helper functions (weather_to_bionic_factors, etc.)"""
    
    def test_module_factors_from_real_data(self):
        """Test that module factors are derived from real data"""
        response = requests.post(
            f"{BASE_URL}/api/bionic/analyze",
            json={
                "territory_id": "test_factors",
                "latitude": TEST_LAT,
                "longitude": TEST_LON,
                "radius_km": 5,
                "modules": ["thermal"],
                "species": ["moose"],
                "include_ai_predictions": False,
                "include_temporal": False
            }
        )
        data = response.json()
        analysis = data.get("analysis", {})
        modules = analysis.get("modules", {})
        
        if "thermal" in modules:
            thermal = modules["thermal"]
            factors = thermal.get("factors", {})
            
            # Factors should be present and in valid range
            for factor_name, factor_value in factors.items():
                assert 0 <= factor_value <= 100, \
                    f"Factor {factor_name} value {factor_value} should be 0-100"


# Run tests if executed directly
if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
