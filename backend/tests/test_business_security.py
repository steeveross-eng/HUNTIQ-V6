"""
Business Dashboard Security Tests - P0 Security
Tests for @require_business_or_admin protection on 20 endpoints

Version: 1.0.0
Date: 2026-02-11

Test Matrix:
- 401: No authentication
- 403: Hunter role (unauthorized)
- 200: Business role (authorized)
- 200: Admin role (authorized)

Endpoints tested:
- Products: POST, PUT, DELETE (3 endpoints)
- Orders: GET list, GET detail, PUT, POST cancel, GET commissions, PUT commission pay (6 endpoints)
- Suppliers: GET list, GET detail, POST, PUT, DELETE (5 endpoints)
- Customers: GET list, GET detail, PUT (3 endpoints)
- Affiliate: GET stats, GET clicks, POST confirm (3 endpoints)
Total: 20 protected endpoints
"""

import pytest
import requests
import os
import uuid

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Test credentials
ADMIN_EMAIL = "steeve.ross@gmail.com"
ADMIN_PASSWORD = "Saturn5858*"
HUNTER_EMAIL = "hunter.test@huntiq.ca"
HUNTER_PASSWORD = "Test1234!"
BUSINESS_EMAIL = "test_9524b5d4@huntiq.ca"
BUSINESS_PASSWORD = "Business123!"


class TestAuthTokens:
    """Helper class to get authentication tokens"""
    
    @staticmethod
    def get_token(email: str, password: str) -> str:
        """Get JWT token for a user"""
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": email, "password": password}
        )
        if response.status_code == 200:
            data = response.json()
            return data.get("token") or data.get("access_token")
        return None


@pytest.fixture(scope="module")
def admin_token():
    """Get admin token"""
    token = TestAuthTokens.get_token(ADMIN_EMAIL, ADMIN_PASSWORD)
    if not token:
        pytest.skip("Could not get admin token")
    return token


@pytest.fixture(scope="module")
def hunter_token():
    """Get hunter token"""
    token = TestAuthTokens.get_token(HUNTER_EMAIL, HUNTER_PASSWORD)
    if not token:
        pytest.skip("Could not get hunter token")
    return token


@pytest.fixture(scope="module")
def business_token():
    """Get business token"""
    token = TestAuthTokens.get_token(BUSINESS_EMAIL, BUSINESS_PASSWORD)
    if not token:
        pytest.skip("Could not get business token")
    return token


@pytest.fixture
def api_client():
    """Shared requests session"""
    session = requests.Session()
    session.headers.update({"Content-Type": "application/json"})
    return session


# ============================================
# PRODUCTS ENGINE TESTS (3 protected endpoints)
# ============================================

class TestProductsSecurityNoAuth:
    """Test products endpoints without authentication - expect 401"""
    
    def test_create_product_no_auth(self, api_client):
        """POST /api/v1/products/ without auth should return 401"""
        response = api_client.post(
            f"{BASE_URL}/api/v1/products/",
            json={"name": "Test Product", "price": 100}
        )
        assert response.status_code == 401, f"Expected 401, got {response.status_code}"
    
    def test_update_product_no_auth(self, api_client):
        """PUT /api/v1/products/{id} without auth should return 401"""
        response = api_client.put(
            f"{BASE_URL}/api/v1/products/test-id",
            json={"name": "Updated Product"}
        )
        assert response.status_code == 401, f"Expected 401, got {response.status_code}"
    
    def test_delete_product_no_auth(self, api_client):
        """DELETE /api/v1/products/{id} without auth should return 401"""
        response = api_client.delete(f"{BASE_URL}/api/v1/products/test-id")
        assert response.status_code == 401, f"Expected 401, got {response.status_code}"


class TestProductsSecurityHunter:
    """Test products endpoints with hunter role - expect 403"""
    
    def test_create_product_hunter(self, api_client, hunter_token):
        """POST /api/v1/products/ with hunter should return 403"""
        api_client.headers.update({"Authorization": f"Bearer {hunter_token}"})
        response = api_client.post(
            f"{BASE_URL}/api/v1/products/",
            json={"name": "Test Product", "price": 100}
        )
        assert response.status_code == 403, f"Expected 403, got {response.status_code}"
    
    def test_update_product_hunter(self, api_client, hunter_token):
        """PUT /api/v1/products/{id} with hunter should return 403"""
        api_client.headers.update({"Authorization": f"Bearer {hunter_token}"})
        response = api_client.put(
            f"{BASE_URL}/api/v1/products/test-id",
            json={"name": "Updated Product"}
        )
        assert response.status_code == 403, f"Expected 403, got {response.status_code}"
    
    def test_delete_product_hunter(self, api_client, hunter_token):
        """DELETE /api/v1/products/{id} with hunter should return 403"""
        api_client.headers.update({"Authorization": f"Bearer {hunter_token}"})
        response = api_client.delete(f"{BASE_URL}/api/v1/products/test-id")
        assert response.status_code == 403, f"Expected 403, got {response.status_code}"


class TestProductsSecurityBusiness:
    """Test products endpoints with business role - expect 200 or 404 (not 401/403)"""
    
    def test_create_product_business(self, api_client, business_token):
        """POST /api/v1/products/ with business should be authorized"""
        api_client.headers.update({"Authorization": f"Bearer {business_token}"})
        response = api_client.post(
            f"{BASE_URL}/api/v1/products/",
            json={
                "name": "TEST_Business_Product",
                "price": 100,
                "category": "test",
                "description": "Test product for security testing"
            }
        )
        # Should not be 401 or 403 - authorization passed
        assert response.status_code not in [401, 403], f"Business should be authorized, got {response.status_code}"
    
    def test_update_product_business(self, api_client, business_token):
        """PUT /api/v1/products/{id} with business should be authorized"""
        api_client.headers.update({"Authorization": f"Bearer {business_token}"})
        response = api_client.put(
            f"{BASE_URL}/api/v1/products/nonexistent-id",
            json={"name": "Updated Product"}
        )
        # 404 is acceptable (product not found), but not 401/403
        assert response.status_code not in [401, 403], f"Business should be authorized, got {response.status_code}"
    
    def test_delete_product_business(self, api_client, business_token):
        """DELETE /api/v1/products/{id} with business should be authorized"""
        api_client.headers.update({"Authorization": f"Bearer {business_token}"})
        response = api_client.delete(f"{BASE_URL}/api/v1/products/nonexistent-id")
        # 404 is acceptable (product not found), but not 401/403
        assert response.status_code not in [401, 403], f"Business should be authorized, got {response.status_code}"


class TestProductsSecurityAdmin:
    """Test products endpoints with admin role - expect 200 or 404 (not 401/403)"""
    
    def test_create_product_admin(self, api_client, admin_token):
        """POST /api/v1/products/ with admin should be authorized"""
        api_client.headers.update({"Authorization": f"Bearer {admin_token}"})
        response = api_client.post(
            f"{BASE_URL}/api/v1/products/",
            json={
                "name": "TEST_Admin_Product",
                "price": 200,
                "category": "test",
                "description": "Test product for admin security testing"
            }
        )
        assert response.status_code not in [401, 403], f"Admin should be authorized, got {response.status_code}"


# ============================================
# ORDERS ENGINE TESTS (6 protected endpoints)
# ============================================

class TestOrdersSecurityNoAuth:
    """Test orders endpoints without authentication - expect 401"""
    
    def test_get_orders_no_auth(self, api_client):
        """GET /api/v1/orders/ without auth should return 401"""
        response = api_client.get(f"{BASE_URL}/api/v1/orders/")
        assert response.status_code == 401, f"Expected 401, got {response.status_code}"
    
    def test_get_order_detail_no_auth(self, api_client):
        """GET /api/v1/orders/{id} without auth should return 401"""
        response = api_client.get(f"{BASE_URL}/api/v1/orders/test-id")
        assert response.status_code == 401, f"Expected 401, got {response.status_code}"
    
    def test_update_order_no_auth(self, api_client):
        """PUT /api/v1/orders/{id} without auth should return 401"""
        response = api_client.put(
            f"{BASE_URL}/api/v1/orders/test-id",
            json={"status": "shipped"}
        )
        assert response.status_code == 401, f"Expected 401, got {response.status_code}"
    
    def test_cancel_order_no_auth(self, api_client):
        """POST /api/v1/orders/{id}/cancel without auth should return 401"""
        response = api_client.post(
            f"{BASE_URL}/api/v1/orders/test-id/cancel",
            json={"reason": "Test cancellation"}
        )
        assert response.status_code == 401, f"Expected 401, got {response.status_code}"
    
    def test_get_commissions_no_auth(self, api_client):
        """GET /api/v1/orders/commissions/ without auth should return 401"""
        response = api_client.get(f"{BASE_URL}/api/v1/orders/commissions/")
        assert response.status_code == 401, f"Expected 401, got {response.status_code}"
    
    def test_pay_commission_no_auth(self, api_client):
        """PUT /api/v1/orders/commissions/{id}/pay without auth should return 401"""
        response = api_client.put(f"{BASE_URL}/api/v1/orders/commissions/test-id/pay")
        assert response.status_code == 401, f"Expected 401, got {response.status_code}"


class TestOrdersSecurityHunter:
    """Test orders endpoints with hunter role - expect 403"""
    
    def test_get_orders_hunter(self, api_client, hunter_token):
        """GET /api/v1/orders/ with hunter should return 403"""
        api_client.headers.update({"Authorization": f"Bearer {hunter_token}"})
        response = api_client.get(f"{BASE_URL}/api/v1/orders/")
        assert response.status_code == 403, f"Expected 403, got {response.status_code}"
    
    def test_get_order_detail_hunter(self, api_client, hunter_token):
        """GET /api/v1/orders/{id} with hunter should return 403"""
        api_client.headers.update({"Authorization": f"Bearer {hunter_token}"})
        response = api_client.get(f"{BASE_URL}/api/v1/orders/test-id")
        assert response.status_code == 403, f"Expected 403, got {response.status_code}"
    
    def test_update_order_hunter(self, api_client, hunter_token):
        """PUT /api/v1/orders/{id} with hunter should return 403"""
        api_client.headers.update({"Authorization": f"Bearer {hunter_token}"})
        response = api_client.put(
            f"{BASE_URL}/api/v1/orders/test-id",
            json={"status": "shipped"}
        )
        assert response.status_code == 403, f"Expected 403, got {response.status_code}"
    
    def test_cancel_order_hunter(self, api_client, hunter_token):
        """POST /api/v1/orders/{id}/cancel with hunter should return 403"""
        api_client.headers.update({"Authorization": f"Bearer {hunter_token}"})
        response = api_client.post(
            f"{BASE_URL}/api/v1/orders/test-id/cancel",
            json={"reason": "Test cancellation"}
        )
        assert response.status_code == 403, f"Expected 403, got {response.status_code}"
    
    def test_get_commissions_hunter(self, api_client, hunter_token):
        """GET /api/v1/orders/commissions/ with hunter should return 403"""
        api_client.headers.update({"Authorization": f"Bearer {hunter_token}"})
        response = api_client.get(f"{BASE_URL}/api/v1/orders/commissions/")
        assert response.status_code == 403, f"Expected 403, got {response.status_code}"
    
    def test_pay_commission_hunter(self, api_client, hunter_token):
        """PUT /api/v1/orders/commissions/{id}/pay with hunter should return 403"""
        api_client.headers.update({"Authorization": f"Bearer {hunter_token}"})
        response = api_client.put(f"{BASE_URL}/api/v1/orders/commissions/test-id/pay")
        assert response.status_code == 403, f"Expected 403, got {response.status_code}"


class TestOrdersSecurityBusiness:
    """Test orders endpoints with business role - expect authorized"""
    
    def test_get_orders_business(self, api_client, business_token):
        """GET /api/v1/orders/ with business should be authorized"""
        api_client.headers.update({"Authorization": f"Bearer {business_token}"})
        response = api_client.get(f"{BASE_URL}/api/v1/orders/")
        assert response.status_code not in [401, 403], f"Business should be authorized, got {response.status_code}"
    
    def test_get_commissions_business(self, api_client, business_token):
        """GET /api/v1/orders/commissions/ with business should be authorized"""
        api_client.headers.update({"Authorization": f"Bearer {business_token}"})
        response = api_client.get(f"{BASE_URL}/api/v1/orders/commissions/")
        assert response.status_code not in [401, 403], f"Business should be authorized, got {response.status_code}"


class TestOrdersSecurityAdmin:
    """Test orders endpoints with admin role - expect authorized"""
    
    def test_get_orders_admin(self, api_client, admin_token):
        """GET /api/v1/orders/ with admin should be authorized"""
        api_client.headers.update({"Authorization": f"Bearer {admin_token}"})
        response = api_client.get(f"{BASE_URL}/api/v1/orders/")
        assert response.status_code not in [401, 403], f"Admin should be authorized, got {response.status_code}"


# ============================================
# SUPPLIERS ENGINE TESTS (5 protected endpoints)
# ============================================

class TestSuppliersSecurityNoAuth:
    """Test suppliers endpoints without authentication - expect 401"""
    
    def test_get_suppliers_no_auth(self, api_client):
        """GET /api/v1/suppliers/ without auth should return 401"""
        response = api_client.get(f"{BASE_URL}/api/v1/suppliers/")
        assert response.status_code == 401, f"Expected 401, got {response.status_code}"
    
    def test_get_supplier_detail_no_auth(self, api_client):
        """GET /api/v1/suppliers/{id} without auth should return 401"""
        response = api_client.get(f"{BASE_URL}/api/v1/suppliers/test-id")
        assert response.status_code == 401, f"Expected 401, got {response.status_code}"
    
    def test_create_supplier_no_auth(self, api_client):
        """POST /api/v1/suppliers/ without auth should return 401"""
        response = api_client.post(
            f"{BASE_URL}/api/v1/suppliers/",
            json={"name": "Test Supplier"}
        )
        assert response.status_code == 401, f"Expected 401, got {response.status_code}"
    
    def test_update_supplier_no_auth(self, api_client):
        """PUT /api/v1/suppliers/{id} without auth should return 401"""
        response = api_client.put(
            f"{BASE_URL}/api/v1/suppliers/test-id",
            json={"name": "Updated Supplier"}
        )
        assert response.status_code == 401, f"Expected 401, got {response.status_code}"
    
    def test_delete_supplier_no_auth(self, api_client):
        """DELETE /api/v1/suppliers/{id} without auth should return 401"""
        response = api_client.delete(f"{BASE_URL}/api/v1/suppliers/test-id")
        assert response.status_code == 401, f"Expected 401, got {response.status_code}"


class TestSuppliersSecurityHunter:
    """Test suppliers endpoints with hunter role - expect 403"""
    
    def test_get_suppliers_hunter(self, api_client, hunter_token):
        """GET /api/v1/suppliers/ with hunter should return 403"""
        api_client.headers.update({"Authorization": f"Bearer {hunter_token}"})
        response = api_client.get(f"{BASE_URL}/api/v1/suppliers/")
        assert response.status_code == 403, f"Expected 403, got {response.status_code}"
    
    def test_get_supplier_detail_hunter(self, api_client, hunter_token):
        """GET /api/v1/suppliers/{id} with hunter should return 403"""
        api_client.headers.update({"Authorization": f"Bearer {hunter_token}"})
        response = api_client.get(f"{BASE_URL}/api/v1/suppliers/test-id")
        assert response.status_code == 403, f"Expected 403, got {response.status_code}"
    
    def test_create_supplier_hunter(self, api_client, hunter_token):
        """POST /api/v1/suppliers/ with hunter should return 403"""
        api_client.headers.update({"Authorization": f"Bearer {hunter_token}"})
        response = api_client.post(
            f"{BASE_URL}/api/v1/suppliers/",
            json={"name": "Test Supplier"}
        )
        assert response.status_code == 403, f"Expected 403, got {response.status_code}"
    
    def test_update_supplier_hunter(self, api_client, hunter_token):
        """PUT /api/v1/suppliers/{id} with hunter should return 403"""
        api_client.headers.update({"Authorization": f"Bearer {hunter_token}"})
        response = api_client.put(
            f"{BASE_URL}/api/v1/suppliers/test-id",
            json={"name": "Updated Supplier"}
        )
        assert response.status_code == 403, f"Expected 403, got {response.status_code}"
    
    def test_delete_supplier_hunter(self, api_client, hunter_token):
        """DELETE /api/v1/suppliers/{id} with hunter should return 403"""
        api_client.headers.update({"Authorization": f"Bearer {hunter_token}"})
        response = api_client.delete(f"{BASE_URL}/api/v1/suppliers/test-id")
        assert response.status_code == 403, f"Expected 403, got {response.status_code}"


class TestSuppliersSecurityBusiness:
    """Test suppliers endpoints with business role - expect authorized"""
    
    def test_get_suppliers_business(self, api_client, business_token):
        """GET /api/v1/suppliers/ with business should be authorized"""
        api_client.headers.update({"Authorization": f"Bearer {business_token}"})
        response = api_client.get(f"{BASE_URL}/api/v1/suppliers/")
        assert response.status_code not in [401, 403], f"Business should be authorized, got {response.status_code}"


# ============================================
# CUSTOMERS ENGINE TESTS (3 protected endpoints)
# ============================================

class TestCustomersSecurityNoAuth:
    """Test customers endpoints without authentication - expect 401"""
    
    def test_get_customers_no_auth(self, api_client):
        """GET /api/v1/customers/ without auth should return 401"""
        response = api_client.get(f"{BASE_URL}/api/v1/customers/")
        assert response.status_code == 401, f"Expected 401, got {response.status_code}"
    
    def test_get_customer_detail_no_auth(self, api_client):
        """GET /api/v1/customers/{id} without auth should return 401"""
        response = api_client.get(f"{BASE_URL}/api/v1/customers/test-id")
        assert response.status_code == 401, f"Expected 401, got {response.status_code}"
    
    def test_update_customer_no_auth(self, api_client):
        """PUT /api/v1/customers/{id} without auth should return 401"""
        response = api_client.put(
            f"{BASE_URL}/api/v1/customers/test-id",
            json={"name": "Updated Customer"}
        )
        assert response.status_code == 401, f"Expected 401, got {response.status_code}"


class TestCustomersSecurityHunter:
    """Test customers endpoints with hunter role - expect 403"""
    
    def test_get_customers_hunter(self, api_client, hunter_token):
        """GET /api/v1/customers/ with hunter should return 403"""
        api_client.headers.update({"Authorization": f"Bearer {hunter_token}"})
        response = api_client.get(f"{BASE_URL}/api/v1/customers/")
        assert response.status_code == 403, f"Expected 403, got {response.status_code}"
    
    def test_get_customer_detail_hunter(self, api_client, hunter_token):
        """GET /api/v1/customers/{id} with hunter should return 403"""
        api_client.headers.update({"Authorization": f"Bearer {hunter_token}"})
        response = api_client.get(f"{BASE_URL}/api/v1/customers/test-id")
        assert response.status_code == 403, f"Expected 403, got {response.status_code}"
    
    def test_update_customer_hunter(self, api_client, hunter_token):
        """PUT /api/v1/customers/{id} with hunter should return 403"""
        api_client.headers.update({"Authorization": f"Bearer {hunter_token}"})
        response = api_client.put(
            f"{BASE_URL}/api/v1/customers/test-id",
            json={"name": "Updated Customer"}
        )
        assert response.status_code == 403, f"Expected 403, got {response.status_code}"


class TestCustomersSecurityBusiness:
    """Test customers endpoints with business role - expect authorized"""
    
    def test_get_customers_business(self, api_client, business_token):
        """GET /api/v1/customers/ with business should be authorized"""
        api_client.headers.update({"Authorization": f"Bearer {business_token}"})
        response = api_client.get(f"{BASE_URL}/api/v1/customers/")
        assert response.status_code not in [401, 403], f"Business should be authorized, got {response.status_code}"


# ============================================
# AFFILIATE ENGINE TESTS (3 protected endpoints)
# ============================================

class TestAffiliateSecurityNoAuth:
    """Test affiliate endpoints without authentication - expect 401"""
    
    def test_get_affiliate_stats_no_auth(self, api_client):
        """GET /api/v1/affiliate/stats without auth should return 401"""
        response = api_client.get(f"{BASE_URL}/api/v1/affiliate/stats")
        assert response.status_code == 401, f"Expected 401, got {response.status_code}"
    
    def test_get_affiliate_clicks_no_auth(self, api_client):
        """GET /api/v1/affiliate/clicks without auth should return 401"""
        response = api_client.get(f"{BASE_URL}/api/v1/affiliate/clicks")
        assert response.status_code == 401, f"Expected 401, got {response.status_code}"
    
    def test_confirm_affiliate_sale_no_auth(self, api_client):
        """POST /api/v1/affiliate/confirm/{id} without auth should return 401"""
        response = api_client.post(
            f"{BASE_URL}/api/v1/affiliate/confirm/test-id",
            params={"commission_amount": 10.0}
        )
        assert response.status_code == 401, f"Expected 401, got {response.status_code}"


class TestAffiliateSecurityHunter:
    """Test affiliate endpoints with hunter role - expect 403"""
    
    def test_get_affiliate_stats_hunter(self, api_client, hunter_token):
        """GET /api/v1/affiliate/stats with hunter should return 403"""
        api_client.headers.update({"Authorization": f"Bearer {hunter_token}"})
        response = api_client.get(f"{BASE_URL}/api/v1/affiliate/stats")
        assert response.status_code == 403, f"Expected 403, got {response.status_code}"
    
    def test_get_affiliate_clicks_hunter(self, api_client, hunter_token):
        """GET /api/v1/affiliate/clicks with hunter should return 403"""
        api_client.headers.update({"Authorization": f"Bearer {hunter_token}"})
        response = api_client.get(f"{BASE_URL}/api/v1/affiliate/clicks")
        assert response.status_code == 403, f"Expected 403, got {response.status_code}"
    
    def test_confirm_affiliate_sale_hunter(self, api_client, hunter_token):
        """POST /api/v1/affiliate/confirm/{id} with hunter should return 403"""
        api_client.headers.update({"Authorization": f"Bearer {hunter_token}"})
        response = api_client.post(
            f"{BASE_URL}/api/v1/affiliate/confirm/test-id",
            params={"commission_amount": 10.0}
        )
        assert response.status_code == 403, f"Expected 403, got {response.status_code}"


class TestAffiliateSecurityBusiness:
    """Test affiliate endpoints with business role - expect authorized"""
    
    def test_get_affiliate_stats_business(self, api_client, business_token):
        """GET /api/v1/affiliate/stats with business should be authorized"""
        api_client.headers.update({"Authorization": f"Bearer {business_token}"})
        response = api_client.get(f"{BASE_URL}/api/v1/affiliate/stats")
        assert response.status_code not in [401, 403], f"Business should be authorized, got {response.status_code}"
    
    def test_get_affiliate_clicks_business(self, api_client, business_token):
        """GET /api/v1/affiliate/clicks with business should be authorized"""
        api_client.headers.update({"Authorization": f"Bearer {business_token}"})
        response = api_client.get(f"{BASE_URL}/api/v1/affiliate/clicks")
        assert response.status_code not in [401, 403], f"Business should be authorized, got {response.status_code}"


# ============================================
# PUBLIC ENDPOINTS TESTS (should remain accessible)
# ============================================

class TestPublicEndpoints:
    """Test that public endpoints remain accessible without auth"""
    
    def test_get_products_public(self, api_client):
        """GET /api/v1/products/ should be public"""
        response = api_client.get(f"{BASE_URL}/api/v1/products/")
        assert response.status_code == 200, f"Products list should be public, got {response.status_code}"
    
    def test_create_order_public(self, api_client):
        """POST /api/v1/orders/ should be public (customers can order)"""
        # This will likely fail validation but should not return 401
        response = api_client.post(
            f"{BASE_URL}/api/v1/orders/",
            json={"product_id": "test", "quantity": 1}
        )
        # Should not be 401 - endpoint is public
        assert response.status_code != 401, f"Order creation should be public, got {response.status_code}"
    
    def test_affiliate_click_public(self, api_client):
        """POST /api/v1/affiliate/click should be public (tracking)"""
        response = api_client.post(
            f"{BASE_URL}/api/v1/affiliate/click",
            params={"product_id": "test", "session_id": "test-session"}
        )
        # Should not be 401 - endpoint is public
        assert response.status_code != 401, f"Affiliate click should be public, got {response.status_code}"
    
    def test_products_health_public(self, api_client):
        """GET /api/v1/products/health should be public"""
        response = api_client.get(f"{BASE_URL}/api/v1/products/health")
        assert response.status_code == 200, f"Products health should be public, got {response.status_code}"
    
    def test_orders_health_public(self, api_client):
        """GET /api/v1/orders/health should be public"""
        response = api_client.get(f"{BASE_URL}/api/v1/orders/health")
        assert response.status_code == 200, f"Orders health should be public, got {response.status_code}"
    
    def test_suppliers_health_public(self, api_client):
        """GET /api/v1/suppliers/health should be public"""
        response = api_client.get(f"{BASE_URL}/api/v1/suppliers/health")
        assert response.status_code == 200, f"Suppliers health should be public, got {response.status_code}"
    
    def test_customers_health_public(self, api_client):
        """GET /api/v1/customers/health should be public"""
        response = api_client.get(f"{BASE_URL}/api/v1/customers/health")
        assert response.status_code == 200, f"Customers health should be public, got {response.status_code}"
    
    def test_affiliate_health_public(self, api_client):
        """GET /api/v1/affiliate/health should be public"""
        response = api_client.get(f"{BASE_URL}/api/v1/affiliate/health")
        assert response.status_code == 200, f"Affiliate health should be public, got {response.status_code}"
    
    def test_customer_create_public(self, api_client):
        """POST /api/v1/customers/ should be public (registration)"""
        response = api_client.post(
            f"{BASE_URL}/api/v1/customers/",
            json={
                "email": f"test_{uuid.uuid4().hex[:8]}@test.com",
                "name": "Test Customer",
                "session_id": f"session_{uuid.uuid4().hex[:8]}"
            }
        )
        # Should not be 401 - endpoint is public
        assert response.status_code != 401, f"Customer creation should be public, got {response.status_code}"
    
    def test_customer_by_session_public(self, api_client):
        """GET /api/v1/customers/session/{id} should be public (self-identification)"""
        response = api_client.get(f"{BASE_URL}/api/v1/customers/session/test-session")
        # 404 is acceptable (session not found), but not 401
        assert response.status_code != 401, f"Customer by session should be public, got {response.status_code}"


# ============================================
# ADMIN ACCESS TESTS
# ============================================

class TestAdminAccessToBusinessEndpoints:
    """Test that admin can access all business endpoints"""
    
    def test_admin_get_orders(self, api_client, admin_token):
        """Admin should access GET /api/v1/orders/"""
        api_client.headers.update({"Authorization": f"Bearer {admin_token}"})
        response = api_client.get(f"{BASE_URL}/api/v1/orders/")
        assert response.status_code == 200, f"Admin should access orders, got {response.status_code}"
    
    def test_admin_get_suppliers(self, api_client, admin_token):
        """Admin should access GET /api/v1/suppliers/"""
        api_client.headers.update({"Authorization": f"Bearer {admin_token}"})
        response = api_client.get(f"{BASE_URL}/api/v1/suppliers/")
        assert response.status_code == 200, f"Admin should access suppliers, got {response.status_code}"
    
    def test_admin_get_customers(self, api_client, admin_token):
        """Admin should access GET /api/v1/customers/"""
        api_client.headers.update({"Authorization": f"Bearer {admin_token}"})
        response = api_client.get(f"{BASE_URL}/api/v1/customers/")
        assert response.status_code == 200, f"Admin should access customers, got {response.status_code}"
    
    def test_admin_get_affiliate_stats(self, api_client, admin_token):
        """Admin should access GET /api/v1/affiliate/stats"""
        api_client.headers.update({"Authorization": f"Bearer {admin_token}"})
        response = api_client.get(f"{BASE_URL}/api/v1/affiliate/stats")
        assert response.status_code == 200, f"Admin should access affiliate stats, got {response.status_code}"
    
    def test_admin_get_commissions(self, api_client, admin_token):
        """Admin should access GET /api/v1/orders/commissions/"""
        api_client.headers.update({"Authorization": f"Bearer {admin_token}"})
        response = api_client.get(f"{BASE_URL}/api/v1/orders/commissions/")
        assert response.status_code == 200, f"Admin should access commissions, got {response.status_code}"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
