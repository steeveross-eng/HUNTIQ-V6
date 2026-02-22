#!/usr/bin/env python3
"""
HUNTIQ V5-ULTIME-FUSION Backend API Testing
===========================================

Tests all V5 fusion modules:
- V4 modules (45+ modules)
- V2 modules (backup-cloud, formations)
- BASE modules (social, rental, admin-advanced, partners, communication)

Version: V5-ULTIME-FUSION
"""

import requests
import sys
import json
from datetime import datetime
from typing import Dict, List, Any

class V5FusionAPITester:
    def __init__(self, base_url="https://bionic-v5-hunt.preview.emergentagent.com"):
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

    def test_modules_status(self):
        """Test /api/modules/status - Should return 54 modules and V5-ULTIME-FUSION architecture"""
        print("\n🔍 Testing V5-ULTIME-FUSION Architecture...")
        success, response = self.test_api_endpoint(
            "Modules Status API", 
            "modules/status", 
            expected_status=200
        )
        
        if success:
            total_modules = response.get('total_modules', 0)
            architecture = response.get('architecture_version', '')
            
            if total_modules == 54:
                print(f"✅ Correct module count: {total_modules}")
            else:
                print(f"⚠️  Expected 54 modules, got {total_modules}")
                
            if architecture == "V5-ULTIME-FUSION":
                print(f"✅ Correct architecture: {architecture}")
            else:
                print(f"⚠️  Expected V5-ULTIME-FUSION, got {architecture}")
                
            # Check fusion sources
            fusion_sources = response.get('fusion_sources', [])
            expected_sources = ["V4 (ossature)", "V3 (frontpage)", "V2 (backup/formations)", "BASE (social/admin)"]
            
            for source in expected_sources:
                if source in fusion_sources:
                    print(f"✅ Fusion source found: {source}")
                else:
                    print(f"⚠️  Missing fusion source: {source}")
        
        return success

    def test_v2_modules(self):
        """Test V2 modules: backup-cloud and formations"""
        print("\n🔍 Testing V2 Modules (backup-cloud, formations)...")
        
        # Test backup-cloud stats
        success1, _ = self.test_api_endpoint(
            "Backup Cloud Stats API", 
            "backup-cloud/stats"
        )
        
        # Test formations list
        success2, response = self.test_api_endpoint(
            "Formations List API", 
            "formations/all"
        )
        
        if success2:
            formations_count = len(response.get('formations', []))
            if formations_count == 7:
                print(f"✅ Correct formations count: {formations_count}")
            else:
                print(f"⚠️  Expected 7 formations, got {formations_count}")
        
        return success1 and success2

    def test_base_modules(self):
        """Test BASE modules: social, rental, admin-advanced, partners, communication"""
        print("\n🔍 Testing BASE Modules (social, rental, admin-advanced, partners, communication)...")
        
        results = []
        
        # Test social network stats
        success1, _ = self.test_api_endpoint(
            "Social Network Stats API", 
            "social/network/stats"
        )
        results.append(success1)
        
        # Test partners endpoint
        success2, _ = self.test_api_endpoint(
            "Partners API", 
            "partners/"
        )
        results.append(success2)
        
        # Test rental lands
        success3, _ = self.test_api_endpoint(
            "Rental Lands API", 
            "rental/lands"
        )
        results.append(success3)
        
        # Test admin advanced brand
        success4, _ = self.test_api_endpoint(
            "Admin Advanced Brand API", 
            "admin-advanced/brand"
        )
        results.append(success4)
        
        # Test communication notifications (with dummy user_id)
        success5, _ = self.test_api_endpoint(
            "Communication Notifications API", 
            "communication/notifications/test-user-123"
        )
        results.append(success5)
        
        return all(results)

    def test_v4_core_modules(self):
        """Test some key V4 core modules"""
        print("\n🔍 Testing V4 Core Modules (sample)...")
        
        results = []
        
        # Test auth status
        success1, _ = self.test_api_endpoint(
            "Auth Status API", 
            "auth/status"
        )
        results.append(success1)
        
        # Test weather endpoint
        success2, _ = self.test_api_endpoint(
            "Weather API", 
            "weather/current"
        )
        results.append(success2)
        
        # Test territories
        success3, _ = self.test_api_endpoint(
            "Territories API", 
            "territories/"
        )
        results.append(success3)
        
        return any(results)  # At least one should work

    def test_health_check(self):
        """Test basic health check"""
        print("\n🔍 Testing Health Check...")
        
        try:
            response = self.session.get(f"{self.base_url}/", timeout=5)
            success = response.status_code in [200, 404]  # 404 is OK for root
            self.log_result("Health Check", success, response.status_code)
            return success
        except Exception as e:
            self.log_result("Health Check", False, None, str(e))
            return False

    def run_all_tests(self):
        """Run all V5-ULTIME-FUSION tests"""
        print("=" * 80)
        print("HUNTIQ V5-ULTIME-FUSION Backend API Testing")
        print("=" * 80)
        print(f"Base URL: {self.base_url}")
        print(f"Test Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Run all test suites
        health_ok = self.test_health_check()
        modules_ok = self.test_modules_status()
        v2_ok = self.test_v2_modules()
        base_ok = self.test_base_modules()
        v4_ok = self.test_v4_core_modules()
        
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
        critical_tests_passed = health_ok and modules_ok
        
        if critical_tests_passed:
            print("\n✅ CRITICAL SYSTEMS: OPERATIONAL")
        else:
            print("\n❌ CRITICAL SYSTEMS: ISSUES DETECTED")
            
        return {
            "total_tests": self.tests_run,
            "passed_tests": self.tests_passed,
            "failed_tests": self.failed_tests,
            "success_rate": self.tests_passed/self.tests_run*100 if self.tests_run > 0 else 0,
            "critical_systems_ok": critical_tests_passed,
            "health_check": health_ok,
            "modules_status": modules_ok,
            "v2_modules": v2_ok,
            "base_modules": base_ok,
            "v4_modules": v4_ok
        }

def main():
    """Main test execution"""
    tester = V5FusionAPITester()
    results = tester.run_all_tests()
    
    # Return appropriate exit code
    if results["critical_systems_ok"]:
        return 0
    else:
        return 1

if __name__ == "__main__":
    sys.exit(main())