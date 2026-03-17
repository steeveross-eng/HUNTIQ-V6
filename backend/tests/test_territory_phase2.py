"""
BIONIC™ Territory Phase 2 API Tests
- GeoJSON API
- Heatmap API
- Scraping Sources API
- Scraping Run API
- Scraping Status API
- Potential Partners API
- Convert to Partner API
"""

import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://organic-zones-map.preview.emergentagent.com')

class TestTerritoryGeoJSON:
    """Test GeoJSON API for map integration"""
    
    def test_geojson_returns_feature_collection(self):
        """GET /api/territories/ai/geojson - should return GeoJSON FeatureCollection"""
        response = requests.get(f"{BASE_URL}/api/territories/ai/geojson")
        assert response.status_code == 200
        
        data = response.json()
        assert data["type"] == "FeatureCollection"
        assert "features" in data
        assert isinstance(data["features"], list)
        assert len(data["features"]) > 0
        
    def test_geojson_feature_structure(self):
        """Verify GeoJSON feature structure"""
        response = requests.get(f"{BASE_URL}/api/territories/ai/geojson")
        assert response.status_code == 200
        
        data = response.json()
        feature = data["features"][0]
        
        # Check feature structure
        assert feature["type"] == "Feature"
        assert "geometry" in feature
        assert "properties" in feature
        
        # Check geometry
        assert feature["geometry"]["type"] == "Point"
        assert "coordinates" in feature["geometry"]
        coords = feature["geometry"]["coordinates"]
        assert len(coords) == 2
        assert isinstance(coords[0], (int, float))  # longitude
        assert isinstance(coords[1], (int, float))  # latitude
        
        # Check properties
        props = feature["properties"]
        assert "id" in props
        assert "name" in props
        assert "province" in props
        assert "global_score" in props
        
    def test_geojson_filter_by_province(self):
        """Test filtering GeoJSON by province"""
        response = requests.get(f"{BASE_URL}/api/territories/ai/geojson?province=QC")
        assert response.status_code == 200
        
        data = response.json()
        for feature in data["features"]:
            assert feature["properties"]["province"] == "QC"
            
    def test_geojson_filter_by_type(self):
        """Test filtering GeoJSON by establishment type"""
        response = requests.get(f"{BASE_URL}/api/territories/ai/geojson?establishment_type=sepaq")
        assert response.status_code == 200
        
        data = response.json()
        for feature in data["features"]:
            assert feature["properties"]["establishment_type"] == "sepaq"


class TestTerritoryHeatmap:
    """Test Heatmap API"""
    
    def test_heatmap_score_metric(self):
        """GET /api/territories/ai/heatmap/score - should return heatmap data"""
        response = requests.get(f"{BASE_URL}/api/territories/ai/heatmap/score")
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] == True
        assert data["metric"] == "score"
        assert "points" in data
        assert isinstance(data["points"], list)
        assert len(data["points"]) > 0
        
    def test_heatmap_point_structure(self):
        """Verify heatmap point structure"""
        response = requests.get(f"{BASE_URL}/api/territories/ai/heatmap/score")
        assert response.status_code == 200
        
        data = response.json()
        point = data["points"][0]
        
        assert "lat" in point
        assert "lon" in point
        assert "value" in point
        assert "name" in point
        assert "id" in point
        
        assert isinstance(point["lat"], (int, float))
        assert isinstance(point["lon"], (int, float))
        assert isinstance(point["value"], (int, float))
        
    def test_heatmap_success_metric(self):
        """Test heatmap with success metric"""
        response = requests.get(f"{BASE_URL}/api/territories/ai/heatmap/success")
        assert response.status_code == 200
        
        data = response.json()
        assert data["metric"] == "success"
        
    def test_heatmap_pressure_metric(self):
        """Test heatmap with pressure metric"""
        response = requests.get(f"{BASE_URL}/api/territories/ai/heatmap/pressure")
        assert response.status_code == 200
        
        data = response.json()
        assert data["metric"] == "pressure"
        
    def test_heatmap_density_metric(self):
        """Test heatmap with density metric"""
        response = requests.get(f"{BASE_URL}/api/territories/ai/heatmap/density")
        assert response.status_code == 200
        
        data = response.json()
        assert data["metric"] == "density"
        
    def test_heatmap_invalid_metric(self):
        """Test heatmap with invalid metric returns 400"""
        response = requests.get(f"{BASE_URL}/api/territories/ai/heatmap/invalid")
        assert response.status_code == 400


class TestScrapingSources:
    """Test Scraping Sources API"""
    
    def test_get_scraping_sources(self):
        """GET /api/territories/scraping/sources - should return list of sources"""
        response = requests.get(f"{BASE_URL}/api/territories/scraping/sources")
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] == True
        assert "sources" in data
        assert isinstance(data["sources"], list)
        assert len(data["sources"]) >= 4  # At least 4 sources configured
        
    def test_source_structure(self):
        """Verify source structure"""
        response = requests.get(f"{BASE_URL}/api/territories/scraping/sources")
        assert response.status_code == 200
        
        data = response.json()
        source = data["sources"][0]
        
        assert "id" in source
        assert "name" in source
        assert "url" in source
        assert "enabled" in source
        
    def test_sources_include_required_sites(self):
        """Verify required scraping sources are configured"""
        response = requests.get(f"{BASE_URL}/api/territories/scraping/sources")
        assert response.status_code == 200
        
        data = response.json()
        source_names = [s["name"].lower() for s in data["sources"]]
        
        # Check for required sources
        assert any("pourvoiries" in name for name in source_names)
        assert any("sepaq" in name or "sépaq" in name for name in source_names)
        assert any("zec" in name for name in source_names)


class TestScrapingRun:
    """Test Scraping Run API"""
    
    def test_run_scraping_sepaq(self):
        """POST /api/territories/scraping/run/sepaq - should start scraping"""
        response = requests.post(f"{BASE_URL}/api/territories/scraping/run/sepaq?limit=5")
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] == True
        assert "message" in data or "status" in data
        
    def test_run_scraping_zec(self):
        """POST /api/territories/scraping/run/zec_quebec - should start scraping"""
        response = requests.post(f"{BASE_URL}/api/territories/scraping/run/zec_quebec?limit=5")
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] == True


class TestScrapingStatus:
    """Test Scraping Status API"""
    
    def test_get_scraping_status(self):
        """GET /api/territories/scraping/status - should return status"""
        response = requests.get(f"{BASE_URL}/api/territories/scraping/status")
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] == True
        assert "status" in data
        
    def test_status_contains_territory_count(self):
        """Verify status contains territory counts"""
        response = requests.get(f"{BASE_URL}/api/territories/scraping/status")
        assert response.status_code == 200
        
        data = response.json()
        status = data["status"]
        
        assert "total_territories" in status
        assert isinstance(status["total_territories"], int)


class TestPotentialPartners:
    """Test Potential Partners API"""
    
    def test_get_potential_partners(self):
        """GET /api/territories/ai/potential-partners - should return list"""
        response = requests.get(f"{BASE_URL}/api/territories/ai/potential-partners?min_score=50&limit=10")
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] == True
        assert "potential_partners" in data
        assert isinstance(data["potential_partners"], list)
        
    def test_potential_partner_structure(self):
        """Verify potential partner structure"""
        response = requests.get(f"{BASE_URL}/api/territories/ai/potential-partners?min_score=50&limit=5")
        assert response.status_code == 200
        
        data = response.json()
        if len(data["potential_partners"]) > 0:
            partner = data["potential_partners"][0]
            
            assert "id" in partner
            assert "name" in partner
            assert "partnership_score" in partner
            assert "partnership_potential" in partner
            
    def test_potential_partners_min_score_filter(self):
        """Test min_score filter works"""
        response = requests.get(f"{BASE_URL}/api/territories/ai/potential-partners?min_score=70&limit=20")
        assert response.status_code == 200
        
        data = response.json()
        for partner in data["potential_partners"]:
            # Check global_score is >= min_score
            global_score = partner.get("scoring", {}).get("global_score", 0)
            assert global_score >= 70


class TestConvertToPartner:
    """Test Convert to Partner API"""
    
    def test_convert_to_partner_success(self):
        """POST /api/territories/ai/{id}/convert-to-partner - should convert territory"""
        # First get a potential partner
        response = requests.get(f"{BASE_URL}/api/territories/ai/potential-partners?min_score=50&limit=1")
        assert response.status_code == 200
        
        data = response.json()
        if len(data["potential_partners"]) > 0:
            partner = data["potential_partners"][0]
            territory_id = partner["id"]
            
            # Try to convert
            convert_response = requests.post(f"{BASE_URL}/api/territories/ai/{territory_id}/convert-to-partner")
            
            # Should succeed or already be a partner
            assert convert_response.status_code in [200, 400]
            
    def test_convert_nonexistent_territory(self):
        """Test converting non-existent territory returns 404"""
        response = requests.post(f"{BASE_URL}/api/territories/ai/nonexistent123/convert-to-partner")
        assert response.status_code == 404


class TestPartnerTerritories:
    """Test Partner Territories API"""
    
    def test_get_partner_territories(self):
        """GET /api/territories/ai/partner-territories - should return partners"""
        response = requests.get(f"{BASE_URL}/api/territories/ai/partner-territories")
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] == True
        assert "partners" in data
        assert isinstance(data["partners"], list)


class TestAIRecommendations:
    """Test AI Recommendations API"""
    
    def test_get_species_recommendations(self):
        """GET /api/territories/ai/recommendations/species/orignal"""
        response = requests.get(f"{BASE_URL}/api/territories/ai/recommendations/species/orignal?month=10&limit=5")
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] == True
        assert "recommendations" in data
        assert "season_info" in data
        
    def test_get_optimal_recommendations(self):
        """GET /api/territories/ai/recommendations/optimal"""
        response = requests.get(f"{BASE_URL}/api/territories/ai/recommendations/optimal?month=10&limit=5")
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] == True
        assert "recommendations" in data
        
    def test_get_hunting_seasons(self):
        """GET /api/territories/ai/seasons"""
        response = requests.get(f"{BASE_URL}/api/territories/ai/seasons")
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] == True
        assert "seasons" in data
        assert "orignal" in data["seasons"]
        assert "chevreuil" in data["seasons"]


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
