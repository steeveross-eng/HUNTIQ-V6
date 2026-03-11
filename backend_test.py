#!/usr/bin/env python3
"""
BIONIC HUNT V6 Backend API Testing
==================================

Tests specific to BIONIC HUNT application:
- BCE API status endpoint
- Zone 2km² backend support
- Corridor 10X with WWF classification
- Territory map loading APIs

Version: V6 BIONIC
"""

import requests
import sys
import json
from datetime import datetime
from typing import Dict, List, Any

class BionicAPITester:
    def __init__(self, base_url="https://huntiq-v5-dev.preview.emergentagent.com"):
        self.base_url = base_url
        self.token = None
        self.tests_run = 0
        self.tests_passed = 0
        self.failed_tests = []
        self.session = requests.Session()
        self.session.headers.update({'Content-Type': 'application/json'})

    def log_result(self, test_name: str, success: bool, status_code: int = None, error: str = None):
        """Log test result"""
        self.tests_run += 1
        if success:
            self.tests_passed += 1
            print(f"✅ {test_name} - PASSED")
        else:
            self.failed_tests.append({
                "test": test_name,
                "status_code": status_code,
                "error": error
            })
            print(f"❌ {test_name} - FAILED (Status: {status_code}, Error: {error})")

    def test_api_endpoint(self, name: str, endpoint: str, method: str = "GET", 
                         data: Dict = None, expected_status: int = 200) -> tuple:
        """Test a single API endpoint"""
        url = f"{self.base_url}/api/{endpoint}"
        
        try:
            if method == "GET":
                response = self.session.get(url, timeout=10)
            elif method == "POST":
                response = self.session.post(url, json=data, timeout=10)
            elif method == "PUT":
                response = self.session.put(url, json=data, timeout=10)
            elif method == "DELETE":
                response = self.session.delete(url, timeout=10)
            
            success = response.status_code == expected_status
            self.log_result(name, success, response.status_code, 
                          None if success else response.text[:200])
            
            return success, response.json() if success and response.content else {}
            
        except requests.exceptions.RequestException as e:
            self.log_result(name, False, None, str(e))
            return False, {}
        except json.JSONDecodeError as e:
            self.log_result(name, False, response.status_code, f"JSON decode error: {str(e)}")
            return False, {}

    def test_health_check(self):
        """Test basic health check"""
        print("\n🔍 Testing Backend Health Check...")
        
        try:
            response = self.session.get(f"{self.base_url}/", timeout=5)
            success = response.status_code in [200, 404]  # 404 is OK for root
            self.log_result("Backend Health Check", success, response.status_code)
            return success
        except Exception as e:
            self.log_result("Backend Health Check", False, None, str(e))
            return False

    def test_bce_api_status(self):
        """Test BCE API status endpoint - Key feature from review request"""
        print("\n🔍 Testing BCE API Status Endpoint...")
        success, response = self.test_api_endpoint(
            "BCE API Status", 
            "bce/status", 
            expected_status=200
        )
        
        if success:
            # Check if response contains expected BCE status information
            status = response.get('status', '')
            if status:
                print(f"✅ BCE API Status: {status}")
            else:
                print("⚠️  BCE API response missing status field")
                
        return success

    def test_territory_map_apis(self):
        """Test territory map loading APIs"""
        print("\n🔍 Testing Territory Map Loading APIs...")
        
        results = []
        
        # Test territories endpoint
        success1, _ = self.test_api_endpoint(
            "Territories API", 
            "territories/",
            expected_status=200
        )
        results.append(success1)
        
        # Test map data endpoint (if exists)
        success2, _ = self.test_api_endpoint(
            "Map Data API", 
            "map/data",
            expected_status=200
        )
        results.append(success2)
        
        # Test bionic zones endpoint (if exists)
        success3, _ = self.test_api_endpoint(
            "Bionic Zones API", 
            "bionic/zones",
            expected_status=200
        )
        results.append(success3)
        
        return any(results)  # At least one should work

    def test_corridor_10x_apis(self):
        """Test Corridor 10X with WWF classification APIs"""
        print("\n🔍 Testing Corridor 10X with WWF Classification...")
        
        results = []
        
        # Test corridors endpoint
        success1, response1 = self.test_api_endpoint(
            "Corridors API", 
            "corridors/",
            expected_status=200
        )
        results.append(success1)
        
        if success1:
            corridors = response1.get('corridors', [])
            print(f"✅ Found {len(corridors)} corridors")
            
            # Check for WWF classification in corridors
            wwf_classified = 0
            for corridor in corridors[:3]:  # Check first 3
                if 'wwf_classification' in corridor:
                    wwf_classified += 1
                    wwf_type = corridor['wwf_classification'].get('type', '')
                    print(f"✅ Corridor WWF Type: {wwf_type}")
            
            if wwf_classified > 0:
                print(f"✅ WWF Classification found in {wwf_classified} corridors")
            else:
                print("⚠️  No WWF classification found in corridors")
        
        # Test corridor classification endpoint
        test_corridor_data = {
            "width_m": 2500,
            "positions": [
                {"lat": 45.5, "lng": -73.6},
                {"lat": 45.51, "lng": -73.59}
            ],
            "fromZoneType": "alimentation",
            "toZoneType": "repos"
        }
        
        success2, response2 = self.test_api_endpoint(
            "Corridor Classification API", 
            "corridors/classify",
            method="POST",
            data=test_corridor_data,
            expected_status=200
        )
        results.append(success2)
        
        if success2:
            wwf_type = response2.get('wwf_classification', {}).get('type', '')
            if wwf_type:
                print(f"✅ Corridor classified as: {wwf_type}")
            else:
                print("⚠️  Corridor classification missing WWF type")
        
        return any(results)

    def test_waypoint_zone_apis(self):
        """Test waypoint and zone related APIs for 2km² zones"""
        print("\n🔍 Testing Waypoint & Zone APIs for 2km² Feature...")
        
        results = []
        
        # Test waypoints API
        success1, response1 = self.test_api_endpoint(
            "Waypoints API", 
            "waypoints/",
            expected_status=200
        )
        results.append(success1)
        
        if success1:
            waypoints = response1.get('waypoints', [])
            print(f"✅ Found {len(waypoints)} waypoints")
        
        # Test zones calculation API (for 2km² zones)
        test_waypoint = {
            "lat": 45.5,
            "lng": -73.6,
            "name": "Test Waypoint"
        }
        
        success2, response2 = self.test_api_endpoint(
            "Zone Calculation API", 
            "zones/calculate",
            method="POST",
            data={"waypoint": test_waypoint, "size_km": 2},
            expected_status=200
        )
        results.append(success2)
        
        if success2:
            zone_bounds = response2.get('bounds', [])
            if len(zone_bounds) == 2:
                print(f"✅ Zone bounds calculated correctly")
            else:
                print("⚠️  Zone bounds format incorrect")
        
        return any(results)

    def run_all_tests(self):
        """Run all BIONIC HUNT V6 tests"""
        print("=" * 80)
        print("BIONIC HUNT V6 Backend API Testing")
        print("=" * 80)
        print(f"Base URL: {self.base_url}")
        print(f"Test Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Run all test suites
        health_ok = self.test_health_check()
        bce_ok = self.test_bce_api_status()
        territory_ok = self.test_territory_map_apis()
        corridor_ok = self.test_corridor_10x_apis()
        zone_ok = self.test_waypoint_zone_apis()
        
        # Print summary
        print("\n" + "=" * 80)
        print("TEST SUMMARY")
        print("=" * 80)
        print(f"Total Tests: {self.tests_run}")
        print(f"Passed: {self.tests_passed}")
        print(f"Failed: {len(self.failed_tests)}")
        print(f"Success Rate: {(self.tests_passed/self.tests_run*100):.1f}%")
        
        if self.failed_tests:
            print("\n❌ FAILED TESTS:")
            for test in self.failed_tests:
                print(f"  - {test['test']}: {test['error']}")
        
        # Overall assessment
        critical_tests_passed = health_ok and bce_ok
        
        if critical_tests_passed:
            print("\n✅ CRITICAL BIONIC SYSTEMS: OPERATIONAL")
        else:
            print("\n❌ CRITICAL BIONIC SYSTEMS: ISSUES DETECTED")
            
        return {
            "total_tests": self.tests_run,
            "passed_tests": self.tests_passed,
            "failed_tests": self.failed_tests,
            "success_rate": self.tests_passed/self.tests_run*100 if self.tests_run > 0 else 0,
            "critical_systems_ok": critical_tests_passed,
            "health_check": health_ok,
            "bce_status": bce_ok,
            "territory_apis": territory_ok,
            "corridor_10x": corridor_ok,
            "zone_apis": zone_ok
        }

def main():
    """Main test execution"""
    tester = BionicAPITester()
    results = tester.run_all_tests()
    
    # Return appropriate exit code
    if results["critical_systems_ok"]:
        return 0
    else:
        return 1

if __name__ == "__main__":
    sys.exit(main())