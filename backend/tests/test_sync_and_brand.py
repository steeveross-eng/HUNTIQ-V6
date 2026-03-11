"""
Test Suite for Bidirectional Sync and Brand Identity APIs
Tests:
- Territory sync status API
- Sync all territories to partnership
- Sync all from partnership to territories
- Brand identity config
- Logo management
- PDF generation
"""

import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

class TestSyncStatus:
    """Test synchronization status endpoint"""
    
    def test_sync_status_returns_data(self):
        """GET /api/territories/sync/status returns sync statistics"""
        response = requests.get(f"{BASE_URL}/api/territories/sync/status")
        assert response.status_code == 200
        
        data = response.json()
        assert data.get('success') is True
        assert 'status' in data
        
        status = data['status']
        assert 'total_territories' in status
        assert 'synced_to_partnership' in status
        assert 'territories_as_partners' in status
        assert 'sync_percentage' in status
        
        # Verify data types
        assert isinstance(status['total_territories'], int)
        assert isinstance(status['synced_to_partnership'], int)
        assert isinstance(status['sync_percentage'], (int, float))
        
        print(f"✓ Sync status: {status['synced_to_partnership']}/{status['total_territories']} ({status['sync_percentage']}%)")
    
    def test_sync_percentage_calculation(self):
        """Verify sync percentage is correctly calculated"""
        response = requests.get(f"{BASE_URL}/api/territories/sync/status")
        assert response.status_code == 200
        
        status = response.json()['status']
        total = status['total_territories']
        synced = status['synced_to_partnership']
        percentage = status['sync_percentage']
        
        if total > 0:
            expected_percentage = round((synced / total * 100), 1)
            assert percentage == expected_percentage, f"Expected {expected_percentage}%, got {percentage}%"
        
        print(f"✓ Sync percentage correctly calculated: {percentage}%")


class TestSyncToPartnership:
    """Test sync territories to partnership endpoint"""
    
    def test_sync_all_to_partnership(self):
        """POST /api/territories/sync/all-to-partnership syncs all territories"""
        response = requests.post(f"{BASE_URL}/api/territories/sync/all-to-partnership")
        assert response.status_code == 200
        
        data = response.json()
        assert data.get('success') is True
        assert 'synced' in data
        assert 'errors' in data
        assert 'total' in data
        
        # Verify counts
        assert isinstance(data['synced'], int)
        assert isinstance(data['errors'], int)
        assert data['synced'] + data['errors'] == data['total']
        
        print(f"✓ Synced {data['synced']}/{data['total']} territories to partnership (errors: {data['errors']})")


class TestSyncFromPartnership:
    """Test sync from partnership to territories endpoint"""
    
    def test_sync_all_from_partnership(self):
        """POST /api/territories/sync/all-from-partnership syncs partner data back"""
        response = requests.post(f"{BASE_URL}/api/territories/sync/all-from-partnership")
        assert response.status_code == 200
        
        data = response.json()
        assert data.get('success') is True
        assert 'synced' in data
        assert 'errors' in data
        assert 'total' in data
        
        print(f"✓ Synced {data['synced']}/{data['total']} partners back to territories (errors: {data['errors']})")


class TestBrandConfig:
    """Test brand identity configuration endpoints"""
    
    def test_get_brand_config(self):
        """GET /api/brand/config returns brand configuration"""
        response = requests.get(f"{BASE_URL}/api/brand/config")
        assert response.status_code == 200
        
        data = response.json()
        assert 'fr' in data
        assert 'en' in data
        
        # Verify French config
        fr = data['fr']
        assert fr['name'] == 'Chasse Bionic™'
        assert 'tagline' in fr
        assert 'slogan' in fr
        assert 'website' in fr
        assert 'email' in fr
        assert 'logo_url' in fr
        
        # Verify English config
        en = data['en']
        assert en['name'] == 'Bionic Hunt™'
        assert 'tagline' in en
        assert 'slogan' in en
        
        print(f"✓ Brand config: FR={fr['name']}, EN={en['name']}")
    
    def test_get_document_templates(self):
        """GET /api/brand/templates returns available templates"""
        response = requests.get(f"{BASE_URL}/api/brand/templates")
        assert response.status_code == 200
        
        data = response.json()
        assert 'templates' in data
        assert len(data['templates']) >= 5
        
        # Verify template structure
        template_ids = [t['id'] for t in data['templates']]
        assert 'letter' in template_ids
        assert 'email' in template_ids
        assert 'contract' in template_ids
        assert 'invoice' in template_ids
        
        print(f"✓ Found {len(data['templates'])} document templates: {template_ids}")
    
    def test_get_logos(self):
        """GET /api/brand/logos returns logo information"""
        response = requests.get(f"{BASE_URL}/api/brand/logos")
        assert response.status_code == 200
        
        data = response.json()
        assert 'official' in data
        assert 'custom' in data
        
        # Verify official logos
        assert 'fr' in data['official']
        assert 'en' in data['official']
        assert data['official']['fr']['exists'] is True
        assert data['official']['en']['exists'] is True
        
        print(f"✓ Official logos exist: FR={data['official']['fr']['exists']}, EN={data['official']['en']['exists']}")


class TestPDFGeneration:
    """Test PDF generation endpoints"""
    
    def test_generate_pdf_letter_fr(self):
        """POST /api/brand/generate-pdf generates French letter PDF"""
        payload = {
            "template_type": "letter",
            "language": "fr",
            "title": "Test Letter",
            "content": "This is a test letter content."
        }
        response = requests.post(f"{BASE_URL}/api/brand/generate-pdf", json=payload)
        assert response.status_code == 200
        assert response.headers.get('content-type') == 'application/pdf'
        
        # Verify PDF content starts with PDF header
        content = response.content
        assert content[:4] == b'%PDF', "Response should be a valid PDF"
        
        print(f"✓ Generated French letter PDF ({len(content)} bytes)")
    
    def test_generate_pdf_letter_en(self):
        """POST /api/brand/generate-pdf generates English letter PDF"""
        payload = {
            "template_type": "letter",
            "language": "en",
            "title": "Test Letter",
            "content": "This is a test letter content."
        }
        response = requests.post(f"{BASE_URL}/api/brand/generate-pdf", json=payload)
        assert response.status_code == 200
        assert response.headers.get('content-type') == 'application/pdf'
        
        content = response.content
        assert content[:4] == b'%PDF', "Response should be a valid PDF"
        
        print(f"✓ Generated English letter PDF ({len(content)} bytes)")
    
    def test_generate_pdf_contract(self):
        """POST /api/brand/generate-pdf generates contract PDF"""
        payload = {
            "template_type": "contract",
            "language": "fr",
            "title": "Contrat de Partenariat",
            "recipient_name": "Test Partner Inc.",
            "recipient_address": "123 Test Street\nMontreal, QC H1A 1A1",
            "content": "Terms and conditions of the partnership agreement."
        }
        response = requests.post(f"{BASE_URL}/api/brand/generate-pdf", json=payload)
        assert response.status_code == 200
        assert response.headers.get('content-type') == 'application/pdf'
        
        print(f"✓ Generated contract PDF ({len(response.content)} bytes)")
    
    def test_generate_pdf_invalid_template(self):
        """POST /api/brand/generate-pdf rejects invalid template"""
        payload = {
            "template_type": "invalid_template",
            "language": "fr"
        }
        response = requests.post(f"{BASE_URL}/api/brand/generate-pdf", json=payload)
        assert response.status_code == 400
        
        print("✓ Invalid template correctly rejected")
    
    def test_generate_pdf_invalid_language(self):
        """POST /api/brand/generate-pdf rejects invalid language"""
        payload = {
            "template_type": "letter",
            "language": "de"  # German not supported
        }
        response = requests.post(f"{BASE_URL}/api/brand/generate-pdf", json=payload)
        assert response.status_code == 400
        
        print("✓ Invalid language correctly rejected")
    
    def test_generate_pdf_get_method(self):
        """GET /api/brand/generate-pdf/{template}/{language} works"""
        response = requests.get(f"{BASE_URL}/api/brand/generate-pdf/letter/fr")
        assert response.status_code == 200
        assert response.headers.get('content-type') == 'application/pdf'
        
        print(f"✓ GET method PDF generation works ({len(response.content)} bytes)")


class TestLogoUpload:
    """Test logo upload functionality"""
    
    def test_get_logo_history(self):
        """GET /api/brand/logo-history returns upload history"""
        response = requests.get(f"{BASE_URL}/api/brand/logo-history")
        assert response.status_code == 200
        
        data = response.json()
        assert 'history' in data
        assert isinstance(data['history'], list)
        
        print(f"✓ Logo history: {len(data['history'])} entries")


class TestTerritoriesBasic:
    """Basic territory API tests"""
    
    def test_list_territories(self):
        """GET /api/territories returns territory list"""
        response = requests.get(f"{BASE_URL}/api/territories")
        assert response.status_code == 200
        
        data = response.json()
        assert data.get('success') is True
        assert 'territories' in data
        assert 'pagination' in data
        
        print(f"✓ Found {len(data['territories'])} territories (total: {data['pagination']['total']})")
    
    def test_get_territory_stats(self):
        """GET /api/territories/stats returns statistics"""
        response = requests.get(f"{BASE_URL}/api/territories/stats")
        assert response.status_code == 200
        
        data = response.json()
        assert data.get('success') is True
        assert 'stats' in data
        
        stats = data['stats']
        assert 'total' in stats
        assert 'by_type' in stats
        assert 'by_province' in stats
        
        print(f"✓ Territory stats: {stats['total']} total, {stats.get('verified', 0)} verified")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
