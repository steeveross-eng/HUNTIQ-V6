"""
BIONIC V3 Hotspots P0 Features Tests
=====================================
Testing the 4 P0 features for Certification Finale:
1. Scheduler annuel endpoint (POST /scheduler/run)
2. Enriched territory data (ville, code_postal, altitude_m, territory_type, access_status, gestionnaire, lot_info, gps)
3. Filtering by territory_type and access_status
4. Territory-types endpoint

NOTE: Must call POST /scheduler/run first to populate hotspots data before testing list/stats endpoints.
"""

import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')
HOTSPOT_API = f"{BASE_URL}/api/v1/admin/bionic-hotspots"

class TestSchedulerEndpoint:
    """Test POST /scheduler/run endpoint - triggers annual extraction"""

    def test_scheduler_run_returns_success(self):
        """POST /scheduler/run should return success with all required fields"""
        response = requests.post(f"{HOTSPOT_API}/scheduler/run", timeout=60)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        assert data.get("success") is True, "Expected success: true"
        assert "scheduler_run" in data, "Missing scheduler_run number"
        assert "total_hotspots" in data, "Missing total_hotspots count"
        assert "next_scheduled" in data, "Missing next_scheduled date"
        assert "bce4x_report" in data, "Missing bce4x_report"
        
        # Verify BCE-4X report structure
        bce = data["bce4x_report"]
        assert bce.get("overall") == "PASS", f"BCE-4X should PASS, got {bce.get('overall')}"
        assert "total_checks" in bce, "Missing total_checks in BCE-4X"
        assert "passed" in bce, "Missing passed count in BCE-4X"
        
        print(f"Scheduler run #{data['scheduler_run']}: {data['total_hotspots']} hotspots, BCE-4X: {bce['overall']} ({bce['passed']}/{bce['total_checks']})")

    def test_scheduler_run_returns_next_year(self):
        """Scheduler should set next_scheduled to year+1"""
        response = requests.post(f"{HOTSPOT_API}/scheduler/run", timeout=60)
        data = response.json()
        
        next_scheduled = data.get("next_scheduled", "")
        # Should be in ISO format with year+1
        assert next_scheduled, "next_scheduled should not be empty"
        import datetime
        current_year = datetime.datetime.now().year
        assert str(current_year + 1) in next_scheduled, f"next_scheduled should contain year {current_year + 1}"
        print(f"Next scheduled: {next_scheduled}")


class TestSchedulerStatus:
    """Test GET /scheduler/status endpoint"""

    def test_scheduler_status_returns_config(self):
        """GET /scheduler/status should return scheduler config"""
        response = requests.get(f"{HOTSPOT_API}/scheduler/status", timeout=30)
        assert response.status_code == 200
        
        data = response.json()
        assert "enabled" in data, "Missing 'enabled' field"
        assert "frequency" in data, "Missing 'frequency' field"
        assert data.get("frequency") == "annual", f"Expected annual frequency, got {data.get('frequency')}"
        print(f"Scheduler status: enabled={data.get('enabled')}, frequency={data.get('frequency')}, total_runs={data.get('total_runs')}")


class TestEnrichedTerritoryData:
    """Test GET /list endpoint returns enriched territory data"""

    def test_list_returns_hotspots_with_territory_fields(self):
        """Each hotspot should have all enriched territory fields"""
        response = requests.get(f"{HOTSPOT_API}/list?limit=50", timeout=30)
        assert response.status_code == 200
        
        data = response.json()
        hotspots = data.get("hotspots", [])
        assert len(hotspots) > 0, "No hotspots returned - run scheduler first"
        
        # Check first hotspot for all required fields
        h = hotspots[0]
        required_fields = ["ville", "code_postal", "altitude_m", "territory_type", "access_status", "gestionnaire", "gps"]
        for field in required_fields:
            assert field in h, f"Missing required field: {field}"
        
        # Verify data types
        assert isinstance(h.get("ville"), str), "ville should be string"
        assert isinstance(h.get("code_postal"), str), "code_postal should be string"
        assert isinstance(h.get("altitude_m"), (int, float)), "altitude_m should be numeric"
        assert isinstance(h.get("territory_type"), str), "territory_type should be string"
        assert isinstance(h.get("access_status"), str), "access_status should be string"
        assert isinstance(h.get("gestionnaire"), dict), "gestionnaire should be dict"
        assert isinstance(h.get("gps"), dict), "gps should be dict"
        
        print(f"Sample hotspot {h['id']}: ville={h['ville']}, territory={h['territory_type']}, access={h['access_status']}")

    def test_list_hotspot_gps_structure(self):
        """GPS field should have lat and lng"""
        response = requests.get(f"{HOTSPOT_API}/list?limit=10", timeout=30)
        data = response.json()
        hotspots = data.get("hotspots", [])
        
        for h in hotspots:
            gps = h.get("gps", {})
            assert "lat" in gps, f"Hotspot {h['id']} GPS missing lat"
            assert "lng" in gps, f"Hotspot {h['id']} GPS missing lng"
            assert isinstance(gps["lat"], (int, float)), "GPS lat should be numeric"
            assert isinstance(gps["lng"], (int, float)), "GPS lng should be numeric"


class TestGestionnaireData:
    """Test gestionnaire field structure for different territory types"""

    def test_gestionnaire_zec_has_contact_info(self):
        """ZEC gestionnaire should have nom, tel, courriel, web"""
        response = requests.get(f"{HOTSPOT_API}/list?territory_type=ZEC&limit=50", timeout=30)
        data = response.json()
        hotspots = data.get("hotspots", [])
        
        if not hotspots:
            pytest.skip("No ZEC territory hotspots found")
        
        h = hotspots[0]
        g = h.get("gestionnaire", {})
        assert g.get("type") == "ZEC", f"Expected type ZEC, got {g.get('type')}"
        assert "nom" in g, "ZEC gestionnaire missing 'nom'"
        assert "tel" in g, "ZEC gestionnaire missing 'tel'"
        assert "courriel" in g, "ZEC gestionnaire missing 'courriel'"
        assert "web" in g, "ZEC gestionnaire missing 'web'"
        print(f"ZEC gestionnaire: {g.get('nom')}, tel={g.get('tel')}")

    def test_gestionnaire_gouvernemental_has_ministere_reglements(self):
        """Gouvernemental gestionnaire should have ministere and reglements"""
        response = requests.get(f"{HOTSPOT_API}/list?territory_type=Gouvernemental&limit=50", timeout=30)
        data = response.json()
        hotspots = data.get("hotspots", [])
        
        if not hotspots:
            pytest.skip("No Gouvernemental territory hotspots found")
        
        h = hotspots[0]
        g = h.get("gestionnaire", {})
        assert g.get("type") == "Gouvernemental", f"Expected type Gouvernemental"
        assert "nom" in g, "Gouvernemental gestionnaire missing 'nom'"
        assert "reglements" in g, "Gouvernemental gestionnaire missing 'reglements'"
        assert "web" in g, "Gouvernemental gestionnaire missing 'web'"
        print(f"Gouvernemental: {g.get('nom')[:50]}...")

    def test_gestionnaire_prive_has_lot_info(self):
        """Prive territory should have lot_info"""
        response = requests.get(f"{HOTSPOT_API}/list?territory_type=Prive&limit=50", timeout=30)
        data = response.json()
        hotspots = data.get("hotspots", [])
        
        if not hotspots:
            pytest.skip("No Prive territory hotspots found")
        
        h = hotspots[0]
        lot = h.get("lot_info", {})
        assert lot is not None, "Prive territory should have lot_info"
        assert "numero_lot" in lot, "lot_info missing numero_lot"
        assert "registre_foncier" in lot, "lot_info missing registre_foncier"
        print(f"Prive lot: {lot.get('numero_lot')}, registre: {lot.get('registre_foncier')[:50]}...")


class TestTerritoryFilters:
    """Test filtering by territory_type and access_status"""

    def test_filter_by_territory_type_zec(self):
        """Filter territory_type=ZEC should return only ZEC hotspots"""
        response = requests.get(f"{HOTSPOT_API}/list?territory_type=ZEC&limit=100", timeout=30)
        assert response.status_code == 200
        
        data = response.json()
        hotspots = data.get("hotspots", [])
        
        if hotspots:
            for h in hotspots:
                assert h.get("territory_type") == "ZEC", f"Expected ZEC, got {h.get('territory_type')}"
            print(f"Found {len(hotspots)} ZEC hotspots")
        else:
            print("No ZEC hotspots found in current extraction")

    def test_filter_by_access_status_payant(self):
        """Filter access_status=Payant should return only Payant access hotspots"""
        response = requests.get(f"{HOTSPOT_API}/list?access_status=Payant&limit=100", timeout=30)
        assert response.status_code == 200
        
        data = response.json()
        hotspots = data.get("hotspots", [])
        
        if hotspots:
            for h in hotspots:
                assert h.get("access_status") == "Payant", f"Expected Payant, got {h.get('access_status')}"
            print(f"Found {len(hotspots)} Payant access hotspots")
        else:
            print("No Payant access hotspots found")

    def test_filter_by_territory_type_reserve_faunique(self):
        """Filter territory_type=Reserve faunique should work"""
        response = requests.get(f"{HOTSPOT_API}/list?territory_type=Reserve faunique&limit=100", timeout=30)
        assert response.status_code == 200
        
        data = response.json()
        print(f"Found {len(data.get('hotspots', []))} Reserve faunique hotspots")


class TestTerritoryTypesEndpoint:
    """Test GET /territory-types endpoint"""

    def test_territory_types_returns_available_types(self):
        """Should return list of available territory types and access statuses"""
        response = requests.get(f"{HOTSPOT_API}/territory-types", timeout=30)
        assert response.status_code == 200
        
        data = response.json()
        assert "territory_types" in data, "Missing territory_types list"
        assert "access_statuses" in data, "Missing access_statuses list"
        
        # Verify expected types
        types = data["territory_types"]
        expected_types = ["Prive", "Public", "Gouvernemental", "ZEC", "Pourvoirie", "Reserve faunique", "Territoire autochtone"]
        for t in expected_types:
            assert t in types, f"Missing territory type: {t}"
        
        statuses = data["access_statuses"]
        expected_statuses = ["Libre", "Restreint", "Payant", "Permission requise"]
        for s in expected_statuses:
            assert s in statuses, f"Missing access status: {s}"
        
        print(f"Territory types: {types}")
        print(f"Access statuses: {statuses}")

    def test_territory_types_returns_distribution(self):
        """Should return distribution of hotspots by type after extraction"""
        response = requests.get(f"{HOTSPOT_API}/territory-types", timeout=30)
        data = response.json()
        
        dist_type = data.get("distribution_by_type", {})
        dist_access = data.get("distribution_by_access", {})
        
        if dist_type:
            print(f"Distribution by type: {dist_type}")
        if dist_access:
            print(f"Distribution by access: {dist_access}")


class TestExtractionSummary:
    """Test extraction summary data (for frontend display)"""

    def test_extraction_returns_regions_summary_with_counts(self):
        """Extraction should return summary with MAJEUR/FORT counts per region"""
        response = requests.post(f"{HOTSPOT_API}/scheduler/run", timeout=60)
        data = response.json()
        
        regions = data.get("regions_summary", [])
        assert len(regions) == 12, f"Expected 12 regions, got {len(regions)}"
        
        total_majeur = 0
        total_fort = 0
        for r in regions:
            assert "majeur" in r, f"Region {r['region_id']} missing majeur count"
            assert "fort" in r, f"Region {r['region_id']} missing fort count"
            total_majeur += r.get("majeur", 0)
            total_fort += r.get("fort", 0)
        
        print(f"Total: {data['total_hotspots']} hotspots, {total_majeur} MAJEUR, {total_fort} FORT")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
