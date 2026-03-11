#!/usr/bin/env python3
"""
BIONIC V8 - Ecological System Backend Test Suite
===============================================
Testing all BIONIC V8 ecological features as specified:
- API GET /api/v1/ecological/species returns 3 species
- API GET /api/v1/ecological/species/orignal/zones returns zones
- API GET /api/v1/ecological/corridors/summary returns WWF summary
- BCE status operational
- All ecological APIs functional

VERSION: 8.0.0 — Backend testing for ecological system
"""

import requests
import sys
import json
from datetime import datetime
from typing import Dict, Any, List, Optional

class BionicV8EcologicalTester:
    def __init__(self, base_url: str = "https://huntiq-v5-dev.preview.emergentagent.com"):
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'User-Agent': 'BIONIC-V8-Test-Suite/1.0'
        })
        self.tests_run = 0
        self.tests_passed = 0
        self.detailed_results = []

    def log_test(self, name: str, passed: bool, details: Dict[str, Any] = None):
        """Log test result with details"""
        self.tests_run += 1
        if passed:
            self.tests_passed += 1
            print(f"✅ {name}")
        else:
            print(f"❌ {name}")
        
        if details:
            print(f"   Details: {details}")
        
        self.detailed_results.append({
            "test_name": name,
            "passed": passed,
            "details": details or {},
            "timestamp": datetime.now().isoformat()
        })

    def test_basic_connectivity(self) -> bool:
        """Test basic API connectivity"""
        try:
            response = self.session.get(f"{self.base_url}/api/health", timeout=10)
            health_data = response.json()
            
            passed = response.status_code == 200 and health_data.get("status") == "healthy"
            self.log_test("Basic API Connectivity", passed, {
                "status_code": response.status_code,
                "health_status": health_data.get("status")
            })
            return passed
        except Exception as e:
            self.log_test("Basic API Connectivity", False, {"error": str(e)})
            return False

    def test_ecological_species_list(self) -> bool:
        """Test GET /api/v1/ecological/species returns 3 species"""
        try:
            response = self.session.get(f"{self.base_url}/api/v1/ecological/species", timeout=10)
            
            if response.status_code != 200:
                self.log_test("Ecological Species List API", False, {
                    "status_code": response.status_code,
                    "error": response.text
                })
                return False
            
            data = response.json()
            species_list = data.get("species", [])
            species_count = len(species_list)
            
            # Check for exactly 3 species
            expected_species = ["orignal", "chevreuil", "ours_noir"]
            found_species = [sp.get("id") for sp in species_list]
            
            passed = (
                species_count == 3 and 
                all(sp in found_species for sp in expected_species)
            )
            
            self.log_test("Ecological Species List (3 species)", passed, {
                "status_code": response.status_code,
                "species_count": species_count,
                "expected": expected_species,
                "found": found_species,
                "version": data.get("version")
            })
            
            return passed
            
        except Exception as e:
            self.log_test("Ecological Species List API", False, {"error": str(e)})
            return False

    def test_orignal_zones_api(self) -> bool:
        """Test GET /api/v1/ecological/species/orignal/zones returns zones"""
        try:
            response = self.session.get(f"{self.base_url}/api/v1/ecological/species/orignal/zones", timeout=10)
            
            if response.status_code != 200:
                self.log_test("Orignal Zones API", False, {
                    "status_code": response.status_code,
                    "error": response.text
                })
                return False
            
            data = response.json()
            zones = data.get("zones", {})
            zones_count = len(zones)
            
            # Check for required zone types
            expected_zones = ["alimentation", "repos", "rut", "corridor"]
            found_zones = list(zones.keys())
            
            # Validate zone structure
            has_valid_structure = True
            for zone_name, zone_data in zones.items():
                required_fields = ["description", "functional_role", "habitat", "criteria"]
                if not all(field in zone_data for field in required_fields):
                    has_valid_structure = False
                    break
            
            passed = (
                zones_count >= 4 and
                all(zone in found_zones for zone in expected_zones) and
                has_valid_structure
            )
            
            self.log_test("Orignal Zones API", passed, {
                "status_code": response.status_code,
                "zones_count": zones_count,
                "expected_zones": expected_zones,
                "found_zones": found_zones,
                "has_valid_structure": has_valid_structure
            })
            
            return passed
            
        except Exception as e:
            self.log_test("Orignal Zones API", False, {"error": str(e)})
            return False

    def test_corridors_summary_api(self) -> bool:
        """Test GET /api/v1/ecological/corridors/summary returns WWF summary"""
        try:
            response = self.session.get(f"{self.base_url}/api/v1/ecological/corridors/summary", timeout=10)
            
            if response.status_code != 200:
                self.log_test("Corridors Summary WWF API", False, {
                    "status_code": response.status_code,
                    "error": response.text
                })
                return False
            
            data = response.json()
            summary = data.get("summary", {})
            by_species = data.get("by_species", {})
            wwf_legend = data.get("wwf_legend", {})
            
            # Check WWF corridor types
            expected_wwf_types = ["macro_corridors", "biological_corridors", "conservation_corridors"]
            wwf_counts_valid = all(wwf_type in summary for wwf_type in expected_wwf_types)
            
            # Check species data
            expected_species = ["orignal", "chevreuil", "ours_noir"]
            species_data_valid = all(sp in by_species for sp in expected_species)
            
            # Check WWF legend structure
            expected_legend_keys = ["macro_corridor", "biological_corridor", "conservation_corridor"]
            legend_valid = all(key in wwf_legend for key in expected_legend_keys)
            
            passed = (
                wwf_counts_valid and 
                species_data_valid and 
                legend_valid and
                summary.get("total_corridors", 0) > 0
            )
            
            self.log_test("Corridors Summary WWF API", passed, {
                "status_code": response.status_code,
                "total_corridors": summary.get("total_corridors", 0),
                "wwf_counts_valid": wwf_counts_valid,
                "species_data_valid": species_data_valid,
                "legend_valid": legend_valid,
                "wwf_types_found": list(summary.keys())
            })
            
            return passed
            
        except Exception as e:
            self.log_test("Corridors Summary WWF API", False, {"error": str(e)})
            return False

    def test_bce_status(self) -> bool:
        """Test BCE status operational"""
        try:
            response = self.session.get(f"{self.base_url}/api/bce/status", timeout=10)
            
            if response.status_code != 200:
                self.log_test("BCE Status API", False, {
                    "status_code": response.status_code,
                    "error": response.text
                })
                return False
            
            data = response.json()
            status = data.get("status", "")
            
            # BCE should be operational
            passed = status.lower() in ["operational", "active", "healthy"]
            
            self.log_test("BCE Status Operational", passed, {
                "status_code": response.status_code,
                "bce_status": status,
                "expected": "operational/active/healthy"
            })
            
            return passed
            
        except Exception as e:
            self.log_test("BCE Status API", False, {"error": str(e)})
            return False

    def test_ecological_validation_api(self) -> bool:
        """Test POST /api/v1/ecological/validate works correctly"""
        try:
            test_data = {
                "species": "orignal",
                "zone_type": "alimentation",
                "season": "automne",
                "ndvi": 0.6,
                "slope": 10,
                "distance_to_water": 300,
                "human_pressure": 0.2
            }
            
            response = self.session.post(
                f"{self.base_url}/api/v1/ecological/validate",
                json=test_data,
                timeout=10
            )
            
            if response.status_code != 200:
                self.log_test("Ecological Validation API", False, {
                    "status_code": response.status_code,
                    "error": response.text
                })
                return False
            
            data = response.json()
            
            # Check validation result structure
            expected_fields = ["global_status", "global_score", "validators_run", "results"]
            has_valid_structure = all(field in data for field in expected_fields)
            
            passed = (
                has_valid_structure and
                data.get("validators_run", 0) > 0 and
                isinstance(data.get("results", []), list)
            )
            
            self.log_test("Ecological Validation API", passed, {
                "status_code": response.status_code,
                "global_status": data.get("global_status"),
                "validators_run": data.get("validators_run", 0),
                "has_valid_structure": has_valid_structure
            })
            
            return passed
            
        except Exception as e:
            self.log_test("Ecological Validation API", False, {"error": str(e)})
            return False

    def test_specific_zone_api(self) -> bool:
        """Test GET /api/v1/ecological/species/orignal/zones/alimentation"""
        try:
            response = self.session.get(
                f"{self.base_url}/api/v1/ecological/species/orignal/zones/alimentation",
                timeout=10
            )
            
            if response.status_code != 200:
                self.log_test("Specific Zone API", False, {
                    "status_code": response.status_code,
                    "error": response.text
                })
                return False
            
            data = response.json()
            zone_data = data.get("data", {})
            
            # Check for comprehensive ecological data
            expected_sections = [
                "description", "functional_role", "habitat", "topography", 
                "hydrology", "human_pressure", "food_sources", "criteria"
            ]
            
            has_complete_data = all(section in zone_data for section in expected_sections)
            
            # Check NDVI criteria
            criteria = zone_data.get("criteria", {})
            has_ndvi_criteria = all(
                key in criteria for key in ["ndvi_min", "ndvi_max", "ndvi_optimal"]
            )
            
            passed = (
                data.get("species") == "orignal" and
                data.get("zone_type") == "alimentation" and
                has_complete_data and
                has_ndvi_criteria
            )
            
            self.log_test("Specific Zone API (Orignal Alimentation)", passed, {
                "status_code": response.status_code,
                "species": data.get("species"),
                "zone_type": data.get("zone_type"),
                "has_complete_data": has_complete_data,
                "has_ndvi_criteria": has_ndvi_criteria,
                "found_sections": list(zone_data.keys())
            })
            
            return passed
            
        except Exception as e:
            self.log_test("Specific Zone API", False, {"error": str(e)})
            return False

    def run_comprehensive_test(self) -> Dict[str, Any]:
        """Run all BIONIC V8 ecological tests"""
        print("=" * 70)
        print("BIONIC V8 - Ecological System Backend Test Suite")
        print("=" * 70)
        print(f"Testing against: {self.base_url}")
        print("=" * 70)
        
        # Core connectivity test
        if not self.test_basic_connectivity():
            print("❌ Basic connectivity failed. Aborting further tests.")
            return self.generate_report()
        
        # BIONIC V8 Ecological Feature Tests
        print("\n🧪 BIONIC V8 Ecological API Tests:")
        self.test_ecological_species_list()
        self.test_orignal_zones_api()
        self.test_corridors_summary_api()
        self.test_bce_status()
        self.test_ecological_validation_api()
        self.test_specific_zone_api()
        
        return self.generate_report()

    def generate_report(self) -> Dict[str, Any]:
        """Generate test report"""
        success_rate = (self.tests_passed / self.tests_run * 100) if self.tests_run > 0 else 0
        
        print("\n" + "=" * 70)
        print(f"📊 Test Results: {self.tests_passed}/{self.tests_run} passed ({success_rate:.1f}%)")
        print("=" * 70)
        
        # Categorize results
        failed_tests = [r for r in self.detailed_results if not r["passed"]]
        critical_failures = []
        minor_failures = []
        
        for test in failed_tests:
            if "API" in test["test_name"] and any(
                keyword in test["test_name"].lower() 
                for keyword in ["species", "corridors", "bce"]
            ):
                critical_failures.append(test)
            else:
                minor_failures.append(test)
        
        report = {
            "summary": f"BIONIC V8 ecological testing completed: {self.tests_passed}/{self.tests_run} tests passed",
            "success_rate": success_rate,
            "tests_run": self.tests_run,
            "tests_passed": self.tests_passed,
            "critical_failures": critical_failures,
            "minor_failures": minor_failures,
            "all_results": self.detailed_results,
            "base_url": self.base_url,
            "timestamp": datetime.now().isoformat()
        }
        
        return report


def main():
    """Main test execution"""
    import os
    
    # Get backend URL from environment
    backend_url = os.environ.get('REACT_APP_BACKEND_URL', 'https://huntiq-v5-dev.preview.emergentagent.com')
    
    print(f"🔍 Initializing BIONIC V8 Ecological Test Suite...")
    print(f"🌐 Backend URL: {backend_url}")
    
    tester = BionicV8EcologicalTester(backend_url)
    report = tester.run_comprehensive_test()
    
    # Determine exit code
    if report["success_rate"] >= 80:
        print(f"✅ Test suite PASSED - Success rate: {report['success_rate']:.1f}%")
        return 0
    elif len(report["critical_failures"]) == 0:
        print(f"⚠️  Test suite PARTIAL - Success rate: {report['success_rate']:.1f}%")
        print("   Critical APIs working, some minor issues detected")
        return 0
    else:
        print(f"❌ Test suite FAILED - Success rate: {report['success_rate']:.1f}%")
        print("   Critical ecological APIs not working properly")
        return 1


if __name__ == "__main__":
    sys.exit(main())