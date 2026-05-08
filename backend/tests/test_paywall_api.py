"""
Backend API Tests for ALPHA DROP Paywall Features
Tests authentication and subscription requirements for protected endpoints
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://viral-product-scout-1.preview.emergentagent.com')

class TestPublicEndpoints:
    """Test endpoints that should be publicly accessible"""
    
    def test_api_root(self):
        """API root should be accessible"""
        response = requests.get(f"{BASE_URL}/api/")
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "ALPHA DROP" in data["message"]
        print(f"✓ API root accessible: {data['message']}")
    
    def test_get_plans_public(self):
        """GET /api/plans should be publicly accessible"""
        response = requests.get(f"{BASE_URL}/api/plans")
        assert response.status_code == 200
        data = response.json()
        assert "plans" in data
        plans = data["plans"]
        # Verify 3 plans exist: scout, hunter, predator
        assert "scout" in plans
        assert "hunter" in plans
        assert "predator" in plans
        # Verify prices
        assert plans["scout"]["price"] == 29.00
        assert plans["hunter"]["price"] == 79.00
        assert plans["predator"]["price"] == 199.00
        print(f"✓ Plans endpoint public: Scout ${plans['scout']['price']}, Hunter ${plans['hunter']['price']}, Predator ${plans['predator']['price']}")
    
    def test_categories_public(self):
        """GET /api/categories should be publicly accessible"""
        response = requests.get(f"{BASE_URL}/api/categories")
        assert response.status_code == 200
        data = response.json()
        assert "categories" in data
        assert len(data["categories"]) > 0
        print(f"✓ Categories endpoint public: {len(data['categories'])} categories")
    
    def test_data_status_public(self):
        """GET /api/data-status should be publicly accessible"""
        response = requests.get(f"{BASE_URL}/api/data-status")
        assert response.status_code == 200
        data = response.json()
        assert "data_mode" in data
        print(f"✓ Data status endpoint public: mode={data['data_mode']}")


class TestSubscriptionCheck:
    """Test subscription check endpoint"""
    
    def test_subscription_check_nonexistent_email(self):
        """GET /api/subscription/check should return 404 for non-existent email"""
        response = requests.get(f"{BASE_URL}/api/subscription/check?email=nonexistent@test.com")
        assert response.status_code == 404
        data = response.json()
        assert "detail" in data
        print(f"✓ Subscription check returns 404 for non-existent email: {data['detail']}")
    
    def test_subscription_check_missing_email(self):
        """GET /api/subscription/check should require email parameter"""
        response = requests.get(f"{BASE_URL}/api/subscription/check")
        assert response.status_code == 422  # Validation error
        print("✓ Subscription check requires email parameter (422)")


class TestProtectedEndpointsWithoutAuth:
    """Test that protected endpoints return 401 without authentication"""
    
    def test_products_requires_auth(self):
        """GET /api/products should return 401 without auth"""
        response = requests.get(f"{BASE_URL}/api/products")
        assert response.status_code == 401
        data = response.json()
        assert "detail" in data
        print(f"✓ /api/products returns 401 without auth: {data['detail']}")
    
    def test_products_dashboard_requires_auth(self):
        """GET /api/products/dashboard should return 401 without auth"""
        response = requests.get(f"{BASE_URL}/api/products/dashboard")
        assert response.status_code == 401
        data = response.json()
        assert "detail" in data
        print(f"✓ /api/products/dashboard returns 401 without auth: {data['detail']}")
    
    def test_stats_requires_auth(self):
        """GET /api/stats should return 401 without auth"""
        response = requests.get(f"{BASE_URL}/api/stats")
        assert response.status_code == 401
        data = response.json()
        assert "detail" in data
        print(f"✓ /api/stats returns 401 without auth: {data['detail']}")
    
    def test_alerts_requires_auth(self):
        """GET /api/alerts should return 401 without auth"""
        response = requests.get(f"{BASE_URL}/api/alerts")
        assert response.status_code == 401
        data = response.json()
        assert "detail" in data
        print(f"✓ /api/alerts returns 401 without auth: {data['detail']}")
    
    def test_hooks_intelligence_requires_auth(self):
        """GET /api/hooks/intelligence should return 401 without auth"""
        response = requests.get(f"{BASE_URL}/api/hooks/intelligence")
        assert response.status_code == 401
        data = response.json()
        assert "detail" in data
        print(f"✓ /api/hooks/intelligence returns 401 without auth: {data['detail']}")
    
    def test_market_validation_requires_auth(self):
        """GET /api/market/validation should return 401 without auth"""
        response = requests.get(f"{BASE_URL}/api/market/validation")
        assert response.status_code == 401
        data = response.json()
        assert "detail" in data
        print(f"✓ /api/market/validation returns 401 without auth: {data['detail']}")
    
    def test_product_detail_requires_auth(self):
        """GET /api/products/{id} should return 401 without auth"""
        response = requests.get(f"{BASE_URL}/api/products/some-product-id")
        assert response.status_code == 401
        data = response.json()
        assert "detail" in data
        print(f"✓ /api/products/{{id}} returns 401 without auth: {data['detail']}")
    
    def test_refresh_products_requires_auth(self):
        """POST /api/products/refresh should return 401 without auth"""
        response = requests.post(f"{BASE_URL}/api/products/refresh")
        assert response.status_code == 401
        data = response.json()
        assert "detail" in data
        print(f"✓ /api/products/refresh returns 401 without auth: {data['detail']}")


class TestCheckoutEndpoints:
    """Test checkout endpoints (public but require Stripe)"""
    
    def test_checkout_create_invalid_plan(self):
        """POST /api/checkout/create should reject invalid plan"""
        response = requests.post(f"{BASE_URL}/api/checkout/create?plan_id=invalid_plan")
        assert response.status_code == 400
        data = response.json()
        assert "detail" in data
        print(f"✓ Checkout rejects invalid plan: {data['detail']}")
    
    def test_checkout_create_valid_plan_exists(self):
        """POST /api/checkout/create endpoint exists for valid plans"""
        # Note: We don't actually create a checkout session to avoid Stripe charges
        # Just verify the endpoint exists and validates the plan
        response = requests.post(f"{BASE_URL}/api/checkout/create?plan_id=scout")
        # Should either succeed (200) or fail with Stripe error (500), not 404
        assert response.status_code in [200, 500]
        print(f"✓ Checkout endpoint exists for valid plan (status: {response.status_code})")


class TestWatchlistEndpoints:
    """Test watchlist endpoints"""
    
    def test_get_watchlist(self):
        """GET /api/watchlist/{user_id} should work"""
        response = requests.get(f"{BASE_URL}/api/watchlist/test_user_123")
        assert response.status_code == 200
        data = response.json()
        assert "watchlist" in data
        print(f"✓ Watchlist endpoint accessible: {len(data['watchlist'])} items")


class TestBetaEndpoints:
    """Test beta signup endpoints (public)"""
    
    def test_beta_stats(self):
        """GET /api/beta/stats should be publicly accessible"""
        response = requests.get(f"{BASE_URL}/api/beta/stats")
        assert response.status_code == 200
        data = response.json()
        print(f"✓ Beta stats endpoint public: {data}")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
