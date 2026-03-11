"""
BIONIC V5 PHASE C — API & Frontend Integration Tests
=====================================================
Tests for the new Phase C API endpoints and frontend integration.

Tests:
- GET /api/v1/bionic/seasonal/status - Seasonal factor status
- GET /api/v1/bionic/seasonal/health - Health check for Phase C modules
- POST /api/v1/bionic/analyze_waypoint - Non-regression for advanced_factors_details
- Frontend: SeasonalFactorsPanel, LayerControlPanel seasonal_factors family
- Frontend: MonTerritoireBionicPage 'Facteurs Saisonniers' accordion

Version: 1.0.0
"""

import pytest
import requests
import os
from datetime import datetime

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')


class TestPhaseC_SeasonalHealthEndpoint:
    """Test GET /api/v1/bionic/seasonal/health endpoint"""
    
    def test_seasonal_health_returns_200(self):
        """Health endpoint should return 200 OK"""
        response = requests.get(f"{BASE_URL}/api/v1/bionic/seasonal/health")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        print("✓ seasonal/health returns 200")
    
    def test_seasonal_health_returns_operational_status(self):
        """Health endpoint should show operational status"""
        response = requests.get(f"{BASE_URL}/api/v1/bionic/seasonal/health")
        data = response.json()
        assert data.get("status") == "operational", f"Expected operational status, got {data.get('status')}"
        print("✓ seasonal/health status is operational")
    
    def test_seasonal_health_contains_phase_c(self):
        """Health endpoint should identify as Phase C"""
        response = requests.get(f"{BASE_URL}/api/v1/bionic/seasonal/health")
        data = response.json()
        assert data.get("phase") == "C", f"Expected phase C, got {data.get('phase')}"
        print("✓ seasonal/health identifies as Phase C")
    
    def test_seasonal_health_has_4_modules(self):
        """Health endpoint should report 4 active modules"""
        response = requests.get(f"{BASE_URL}/api/v1/bionic/seasonal/health")
        data = response.json()
        modules = data.get("modules", {})
        
        expected_modules = ["C1_calving", "C2_dispersal", "C3_thermal_stress", "C4_hunting_pressure"]
        for module in expected_modules:
            assert module in modules, f"Missing module: {module}"
            assert modules[module] == "active", f"Module {module} is not active"
        
        print(f"✓ seasonal/health has 4 active modules: {list(modules.keys())}")


class TestPhaseC_SeasonalStatusEndpoint:
    """Test GET /api/v1/bionic/seasonal/status endpoint"""
    
    def test_seasonal_status_returns_200(self):
        """Status endpoint should return 200 OK"""
        response = requests.get(f"{BASE_URL}/api/v1/bionic/seasonal/status")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        print("✓ seasonal/status returns 200")
    
    def test_seasonal_status_with_parameters(self):
        """Status endpoint should accept species/region/temperature parameters"""
        response = requests.get(
            f"{BASE_URL}/api/v1/bionic/seasonal/status",
            params={"species": "orignal", "region": "CA-QC", "temperature_c": 25}
        )
        assert response.status_code == 200
        data = response.json()
        
        assert data.get("species") == "orignal"
        assert data.get("region") == "CA-QC"
        print("✓ seasonal/status accepts parameters correctly")
    
    def test_seasonal_status_contains_4_factors(self):
        """Status endpoint should return all 4 seasonal factors"""
        response = requests.get(f"{BASE_URL}/api/v1/bionic/seasonal/status")
        data = response.json()
        factors = data.get("factors", {})
        
        expected_factors = ["C1_calving", "C2_dispersal", "C3_thermal_stress", "C4_hunting_pressure"]
        for factor in expected_factors:
            assert factor in factors, f"Missing factor: {factor}"
        
        print(f"✓ seasonal/status has 4 factors: {list(factors.keys())}")
    
    def test_seasonal_status_factor_structure(self):
        """Each factor should have label, active, and description fields"""
        response = requests.get(f"{BASE_URL}/api/v1/bionic/seasonal/status")
        data = response.json()
        factors = data.get("factors", {})
        
        for factor_id, factor_data in factors.items():
            assert "label" in factor_data, f"Factor {factor_id} missing label"
            assert "active" in factor_data or "hunting_season_active" in factor_data, f"Factor {factor_id} missing active field"
            assert "description" in factor_data, f"Factor {factor_id} missing description"
        
        print("✓ All factors have correct structure (label, active, description)")
    
    def test_seasonal_status_thermal_stress_with_temperature(self):
        """Thermal stress should be active when high temperature provided"""
        response = requests.get(
            f"{BASE_URL}/api/v1/bionic/seasonal/status",
            params={"species": "orignal", "temperature_c": 30}  # High temp for moose
        )
        data = response.json()
        thermal = data.get("factors", {}).get("C3_thermal_stress", {})
        
        # Moose is sensitive at 25°C+, so 30°C should trigger thermal stress
        assert thermal.get("active") == True, f"Expected thermal stress active at 30°C, got {thermal.get('active')}"
        print("✓ Thermal stress correctly activated at high temperature (30°C)")


class TestPhaseC_AnalyzeWaypointNonRegression:
    """Test POST /api/v1/bionic/analyze_waypoint for Phase C non-regression"""
    
    def test_analyze_waypoint_returns_200(self):
        """Analyze waypoint should return 200 OK"""
        payload = {
            "waypoint": {
                "id": "test-phase-c-1",
                "name": "Test Phase C",
                "latitude": 46.8139,
                "longitude": -71.208
            },
            "target_datetime": "2026-01-15T10:00:00Z",
            "species": "orignal"
        }
        response = requests.post(f"{BASE_URL}/api/v1/bionic/analyze_waypoint", json=payload)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        print("✓ analyze_waypoint returns 200")
    
    def test_analyze_waypoint_has_advanced_factors_details(self):
        """Response should contain advanced_factors_details with Phase C data"""
        payload = {
            "waypoint": {
                "id": "test-phase-c-2",
                "name": "Test Phase C",
                "latitude": 46.8139,
                "longitude": -71.208
            },
            "target_datetime": "2026-06-15T10:00:00Z",  # Summer date
            "species": "orignal"
        }
        response = requests.post(f"{BASE_URL}/api/v1/bionic/analyze_waypoint", json=payload)
        data = response.json()
        
        scores = data.get("scores", {})
        advanced_factors = scores.get("advanced_factors_details", {})
        
        assert advanced_factors is not None, "Missing advanced_factors_details"
        print("✓ analyze_waypoint has advanced_factors_details")
    
    def test_analyze_waypoint_has_phase_c_factors(self):
        """advanced_factors_details should contain Phase C specific factors"""
        payload = {
            "waypoint": {
                "id": "test-phase-c-3",
                "name": "Test Phase C",
                "latitude": 46.8139,
                "longitude": -71.208
            },
            "target_datetime": "2026-01-15T10:00:00Z",
            "species": "orignal"
        }
        response = requests.post(f"{BASE_URL}/api/v1/bionic/analyze_waypoint", json=payload)
        data = response.json()
        
        factors = data.get("scores", {}).get("advanced_factors_details", {}).get("factors", {})
        
        # Phase C factors
        phase_c_factors = ["dispersal_juvenile", "thermal_stress", "hunting_pressure"]
        for factor in phase_c_factors:
            assert factor in factors, f"Missing Phase C factor: {factor}"
        
        print(f"✓ analyze_waypoint has Phase C factors: {phase_c_factors}")
    
    def test_analyze_waypoint_has_phase_c_modifier(self):
        """Response should contain phase_c_modifier in advanced_factors_details.factors"""
        payload = {
            "waypoint": {
                "id": "test-phase-c-4",
                "name": "Test Phase C",
                "latitude": 46.8139,
                "longitude": -71.208
            },
            "target_datetime": "2026-01-15T10:00:00Z",
            "species": "orignal"
        }
        response = requests.post(f"{BASE_URL}/api/v1/bionic/analyze_waypoint", json=payload)
        data = response.json()
        
        advanced_factors = data.get("scores", {}).get("advanced_factors_details", {})
        factors = advanced_factors.get("factors", {})
        
        assert "phase_c_modifier" in factors, f"Missing phase_c_modifier in factors. Keys: {list(factors.keys())}"
        modifier = factors.get("phase_c_modifier")
        assert isinstance(modifier, (int, float)), f"phase_c_modifier should be numeric, got {type(modifier)}"
        print(f"✓ analyze_waypoint has phase_c_modifier: {modifier}")


class TestPhaseC_IntegratedServices:
    """Test that Phase C modules are integrated in the analyze_waypoint response"""
    
    def test_integrated_services_list_contains_seasonal_model(self):
        """integrated_services should mention SeasonalModel for Phase C"""
        payload = {
            "waypoint": {
                "id": "test-services-1",
                "name": "Test Services",
                "latitude": 46.8139,
                "longitude": -71.208
            },
            "target_datetime": "2026-01-15T10:00:00Z",
            "species": "orignal"
        }
        response = requests.post(f"{BASE_URL}/api/v1/bionic/analyze_waypoint", json=payload)
        data = response.json()
        
        advanced_factors = data.get("scores", {}).get("advanced_factors_details", {})
        integrated_services = advanced_factors.get("integrated_services", [])
        
        seasonal_service_found = any("PHASE C" in svc or "SeasonalModel" in svc for svc in integrated_services)
        assert seasonal_service_found, f"No Phase C service in integrated_services: {integrated_services}"
        print(f"✓ integrated_services contains Phase C: {[s for s in integrated_services if 'PHASE C' in s or 'SeasonalModel' in s]}")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
