"""
BRANCHE 1 POLISH FINAL - Backend & Frontend Verification Tests
Tests for optimization features: Image conversion, JSON minification, 
performance optimizations, accessibility, recharts removal
"""

import pytest
import requests
import os
import json

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

class TestPolishFinalBackend:
    """Backend health and API tests"""
    
    def test_backend_health(self):
        """Verify backend is healthy"""
        response = requests.get(f"{BASE_URL}/api/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["version"] == "5.0.0"
        assert data["architecture"] == "V5-ULTIME"
        print(f"✓ Backend healthy: {data}")
    
    def test_api_endpoints_accessible(self):
        """Test critical API endpoints are accessible"""
        endpoints = [
            "/api/health",
            "/api/v1/bionic/status",
        ]
        for endpoint in endpoints:
            response = requests.get(f"{BASE_URL}{endpoint}")
            # Should not be 500 or connection error
            assert response.status_code in [200, 401, 404], f"Endpoint {endpoint} returned {response.status_code}"
            print(f"✓ {endpoint}: {response.status_code}")


class TestPolishFinalFiles:
    """File system tests for optimization artifacts"""
    
    def test_json_minification(self):
        """Verify JSON file is minified (single line)"""
        json_path = "/app/frontend/public/V5_ULTIME_FUSION_COMPLETE.json"
        assert os.path.exists(json_path), "JSON file not found"
        
        with open(json_path, 'r') as f:
            content = f.read()
        
        # Count newlines - should be 0 for minified JSON
        newline_count = content.count('\n')
        assert newline_count == 0, f"JSON not minified - contains {newline_count} newlines"
        
        # Verify it's valid JSON
        data = json.loads(content)
        assert "version" in data
        assert data["version"] == "V5-ULTIME-FUSION"
        
        file_size = os.path.getsize(json_path)
        print(f"✓ JSON minified: {file_size} bytes, 0 newlines")
    
    def test_avif_webp_images_exist(self):
        """Verify AVIF and WebP images were generated"""
        logos_dir = "/app/frontend/public/logos"
        assert os.path.isdir(logos_dir), "Logos directory not found"
        
        required_files = [
            "bionic-logo-official.avif",
            "bionic-logo-official.webp",
            "bionic-logo-official.png",  # Fallback
            "bionic-logo-main.avif",
            "bionic-logo-main.webp",
            "bionic-logo-main.png",
        ]
        
        for filename in required_files:
            filepath = os.path.join(logos_dir, filename)
            assert os.path.exists(filepath), f"Missing: {filename}"
            size = os.path.getsize(filepath)
            print(f"✓ {filename}: {size:,} bytes")
    
    def test_image_compression_ratio(self):
        """Verify AVIF/WebP files are significantly smaller than PNG"""
        logos_dir = "/app/frontend/public/logos"
        
        png_file = os.path.join(logos_dir, "bionic-logo-official.png")
        avif_file = os.path.join(logos_dir, "bionic-logo-official.avif")
        webp_file = os.path.join(logos_dir, "bionic-logo-official.webp")
        
        png_size = os.path.getsize(png_file)
        avif_size = os.path.getsize(avif_file)
        webp_size = os.path.getsize(webp_file)
        
        # AVIF should be at least 90% smaller than PNG
        avif_reduction = (1 - avif_size / png_size) * 100
        assert avif_reduction > 90, f"AVIF reduction only {avif_reduction:.1f}%"
        
        # WebP should be at least 90% smaller than PNG
        webp_reduction = (1 - webp_size / png_size) * 100
        assert webp_reduction > 90, f"WebP reduction only {webp_reduction:.1f}%"
        
        print(f"✓ AVIF reduction: {avif_reduction:.1f}% ({png_size:,} → {avif_size:,} bytes)")
        print(f"✓ WebP reduction: {webp_reduction:.1f}% ({png_size:,} → {webp_size:,} bytes)")
    
    def test_recharts_removed_from_package_json(self):
        """Verify recharts is not in package.json"""
        package_json_path = "/app/frontend/package.json"
        assert os.path.exists(package_json_path), "package.json not found"
        
        with open(package_json_path, 'r') as f:
            content = f.read()
        
        assert "recharts" not in content.lower(), "recharts still in package.json!"
        print("✓ recharts removed from package.json")


class TestPolishFinalComponents:
    """Component existence tests"""
    
    def test_optimized_image_component_exists(self):
        """Verify OptimizedImage component exists"""
        component_path = "/app/frontend/src/components/ui/OptimizedImage.jsx"
        assert os.path.exists(component_path), "OptimizedImage.jsx not found"
        
        with open(component_path, 'r') as f:
            content = f.read()
        
        # Check for picture element usage
        assert "<picture>" in content, "OptimizedImage should use <picture> element"
        assert "image/avif" in content, "OptimizedImage should support AVIF"
        assert "image/webp" in content, "OptimizedImage should support WebP"
        print("✓ OptimizedImage component exists with AVIF/WebP support")
    
    def test_performance_optimizations_module_exists(self):
        """Verify performanceOptimizations module exists"""
        module_path = "/app/frontend/src/utils/performanceOptimizations.js"
        assert os.path.exists(module_path), "performanceOptimizations.js not found"
        
        with open(module_path, 'r') as f:
            content = f.read()
        
        # Check for key functions
        assert "initLongTaskObserver" in content, "Missing Long Task Observer"
        assert "upgradePassiveListeners" in content, "Missing passive listeners upgrade"
        assert "initPerformanceOptimizations" in content, "Missing init function"
        assert "version" in content.lower() and "2.0.0" in content, "Should be version 2.0.0"
        print("✓ performanceOptimizations module v2.0.0 exists")
    
    def test_accessibility_enhancements_module_exists(self):
        """Verify accessibilityEnhancements module exists"""
        module_path = "/app/frontend/src/utils/accessibilityEnhancements.js"
        assert os.path.exists(module_path), "accessibilityEnhancements.js not found"
        
        with open(module_path, 'r') as f:
            content = f.read()
        
        # Check for WCAG AAA features
        assert "WCAG" in content, "Missing WCAG reference"
        assert "injectSkipLink" in content, "Missing skip-link injection"
        assert "enhanceFocusVisibility" in content, "Missing focus enhancement"
        assert "initAccessibilityEnhancements" in content, "Missing init function"
        assert "version" in content.lower() and "2.0.0" in content, "Should be version 2.0.0"
        print("✓ accessibilityEnhancements module v2.0.0 exists with WCAG AAA features")
    
    def test_bionic_logo_uses_optimized_image(self):
        """Verify BionicLogo uses OptimizedImage component"""
        component_path = "/app/frontend/src/components/BionicLogo.jsx"
        assert os.path.exists(component_path), "BionicLogo.jsx not found"
        
        with open(component_path, 'r') as f:
            content = f.read()
        
        assert "OptimizedImage" in content, "BionicLogo should use OptimizedImage"
        assert "import OptimizedImage" in content, "BionicLogo should import OptimizedImage"
        print("✓ BionicLogo uses OptimizedImage component")
    
    def test_index_js_initializes_optimizations(self):
        """Verify index.js initializes performance and accessibility modules"""
        index_path = "/app/frontend/src/index.js"
        assert os.path.exists(index_path), "index.js not found"
        
        with open(index_path, 'r') as f:
            content = f.read()
        
        assert "initPerformanceOptimizations" in content, "Missing performance init"
        assert "initAccessibilityEnhancements" in content, "Missing accessibility init"
        assert "serviceWorkerRegistration" in content.lower() or "serviceWorker" in content, "Missing service worker"
        print("✓ index.js initializes all POLISH FINAL optimizations")


class TestPolishFinalFrontend:
    """Frontend endpoint tests via HTTP"""
    
    def test_frontend_homepage_loads(self):
        """Verify frontend homepage returns 200"""
        response = requests.get(BASE_URL)
        assert response.status_code == 200, f"Homepage returned {response.status_code}"
        print("✓ Frontend homepage loads (200)")
    
    def test_frontend_serves_optimized_images(self):
        """Verify optimized images are served"""
        image_urls = [
            "/logos/bionic-logo-official.avif",
            "/logos/bionic-logo-official.webp",
        ]
        for url in image_urls:
            response = requests.head(f"{BASE_URL}{url}")
            assert response.status_code == 200, f"Image {url} returned {response.status_code}"
            print(f"✓ {url}: {response.status_code}")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
