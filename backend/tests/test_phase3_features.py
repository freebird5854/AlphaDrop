"""
Test suite for ALPHA DROP Phase 3 features:
1. Time-series sales forecasting (predict 7/14/30 days out, viral probability)
2. Shopify store tracking (add/remove stores, revenue estimates)
3. Creator Marketplace two-sided (sellers post briefs, creators apply)

All new endpoints require subscription auth (admin JWT works).
"""
import pytest
import requests
import os
import uuid

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Test credentials
ADMIN_EMAIL = "admin@alphadrop.com"
ADMIN_PASSWORD = "AlphaDr0p!2026"


class TestAdminLogin:
    """Verify admin login still works and get token for subsequent tests"""
    
    def test_admin_login_returns_token(self):
        """POST /api/admin/login with correct credentials returns JWT token"""
        response = requests.post(
            f"{BASE_URL}/api/admin/login",
            json={"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD}
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        assert "token" in data, "Response should contain 'token'"
        assert data["email"] == ADMIN_EMAIL.lower(), f"Email mismatch: {data['email']}"
        print(f"✓ Admin login works: {data['email']}")


@pytest.fixture(scope="module")
def admin_token():
    """Get admin JWT token for authenticated requests"""
    response = requests.post(
        f"{BASE_URL}/api/admin/login",
        json={"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD}
    )
    assert response.status_code == 200, f"Admin login failed: {response.text}"
    return response.json()["token"]


@pytest.fixture(scope="module")
def product_id(admin_token):
    """Get a valid product ID for testing forecast endpoint"""
    response = requests.get(
        f"{BASE_URL}/api/products?limit=1",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 200, f"Failed to get products: {response.text}"
    data = response.json()
    # API returns list directly, not wrapped in {"products": [...]}
    products = data if isinstance(data, list) else data.get("products", [])
    assert len(products) > 0, "No products found in database"
    return products[0]["id"]


# ============================================================================
# FORECAST ENDPOINTS TESTS
# ============================================================================

class TestForecastEndpointsNoAuth:
    """Test /api/forecast endpoints without authentication - should return 401"""
    
    def test_forecast_product_returns_401_without_auth(self):
        """GET /api/forecast/product/{id} should return 401 without auth"""
        response = requests.get(f"{BASE_URL}/api/forecast/product/some-id")
        assert response.status_code == 401, f"Expected 401, got {response.status_code}: {response.text}"
        print("✓ GET /api/forecast/product/{id} returns 401 without auth")
    
    def test_top_forecasts_returns_401_without_auth(self):
        """GET /api/forecast/top-forecasts should return 401 without auth"""
        response = requests.get(f"{BASE_URL}/api/forecast/top-forecasts")
        assert response.status_code == 401, f"Expected 401, got {response.status_code}: {response.text}"
        print("✓ GET /api/forecast/top-forecasts returns 401 without auth")


class TestForecastEndpointsWithAuth:
    """Test /api/forecast endpoints with admin authentication"""
    
    def test_forecast_product_returns_forecast_with_metrics(self, admin_token, product_id):
        """GET /api/forecast/product/{id} returns forecast with metrics (requires auth)"""
        response = requests.get(
            f"{BASE_URL}/api/forecast/product/{product_id}",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        
        # Verify response structure
        assert "product_id" in data, "Response should contain 'product_id'"
        assert "product_name" in data, "Response should contain 'product_name'"
        assert "forecast" in data, "Response should contain 'forecast'"
        assert "metrics" in data, "Response should contain 'metrics'"
        assert "historical" in data, "Response should contain 'historical'"
        
        # Verify metrics structure
        metrics = data.get("metrics", {})
        if metrics:  # May be empty if no trend data
            expected_metric_keys = ["current_daily_sales", "7d_avg_sales", "forecast_7d_total", 
                                   "forecast_14d_total", "forecast_30d_total", "viral_probability"]
            for key in expected_metric_keys:
                assert key in metrics, f"Metrics should contain '{key}'"
        
        print(f"✓ GET /api/forecast/product/{product_id} returns forecast with metrics")
        print(f"  Product: {data['product_name']}, Status: {data.get('status')}")
        if metrics:
            print(f"  Viral Probability: {metrics.get('viral_probability')}")
    
    def test_forecast_product_with_custom_days(self, admin_token, product_id):
        """GET /api/forecast/product/{id}?days=30 returns 30-day forecast"""
        response = requests.get(
            f"{BASE_URL}/api/forecast/product/{product_id}?days=30",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        forecast = data.get("forecast", [])
        # Forecast length depends on available trend data
        print(f"✓ GET /api/forecast/product/{product_id}?days=30 returns {len(forecast)} day forecast")
    
    def test_forecast_product_returns_404_for_invalid_id(self, admin_token):
        """GET /api/forecast/product/{invalid_id} returns 404"""
        response = requests.get(
            f"{BASE_URL}/api/forecast/product/invalid-product-id-12345",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 404, f"Expected 404, got {response.status_code}: {response.text}"
        print("✓ GET /api/forecast/product/{invalid_id} returns 404")
    
    def test_top_forecasts_returns_ranked_products(self, admin_token):
        """GET /api/forecast/top-forecasts returns ranked products by 7d forecast (requires auth)"""
        response = requests.get(
            f"{BASE_URL}/api/forecast/top-forecasts",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        
        assert "forecasts" in data, "Response should contain 'forecasts'"
        forecasts = data["forecasts"]
        
        if len(forecasts) > 0:
            # Verify forecast item structure
            first = forecasts[0]
            assert "product_id" in first, "Forecast item should contain 'product_id'"
            assert "product_name" in first, "Forecast item should contain 'product_name'"
            assert "forecast_7d" in first, "Forecast item should contain 'forecast_7d'"
            assert "viral_probability" in first, "Forecast item should contain 'viral_probability'"
            
            # Verify sorted by forecast_7d descending
            if len(forecasts) > 1:
                for i in range(len(forecasts) - 1):
                    assert forecasts[i]["forecast_7d"] >= forecasts[i+1]["forecast_7d"], \
                        "Forecasts should be sorted by forecast_7d descending"
        
        print(f"✓ GET /api/forecast/top-forecasts returns {len(forecasts)} ranked products")


# ============================================================================
# STORE TRACKING ENDPOINTS TESTS
# ============================================================================

class TestStoreTrackingEndpointsNoAuth:
    """Test /api/stores endpoints without authentication - should return 401"""
    
    def test_stores_returns_401_without_auth(self):
        """GET /api/stores should return 401 without auth"""
        response = requests.get(f"{BASE_URL}/api/stores")
        assert response.status_code == 401, f"Expected 401, got {response.status_code}: {response.text}"
        print("✓ GET /api/stores returns 401 without auth")
    
    def test_add_store_returns_401_without_auth(self):
        """POST /api/stores/add should return 401 without auth"""
        response = requests.post(
            f"{BASE_URL}/api/stores/add",
            json={"store_url": "https://test-store.myshopify.com", "name": "Test Store"}
        )
        assert response.status_code == 401, f"Expected 401, got {response.status_code}: {response.text}"
        print("✓ POST /api/stores/add returns 401 without auth")
    
    def test_delete_store_returns_401_without_auth(self):
        """DELETE /api/stores/{id} should return 401 without auth"""
        response = requests.delete(f"{BASE_URL}/api/stores/some-store-id")
        assert response.status_code == 401, f"Expected 401, got {response.status_code}: {response.text}"
        print("✓ DELETE /api/stores/{id} returns 401 without auth")


class TestStoreTrackingEndpointsWithAuth:
    """Test /api/stores endpoints with admin authentication"""
    
    def test_add_store_creates_tracked_store(self, admin_token):
        """POST /api/stores/add creates a tracked store (requires auth)"""
        unique_url = f"https://test-store-{uuid.uuid4().hex[:8]}.myshopify.com"
        response = requests.post(
            f"{BASE_URL}/api/stores/add",
            headers={"Authorization": f"Bearer {admin_token}"},
            json={"store_url": unique_url, "name": "TEST_Phase3_Store"}
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        
        assert "message" in data, "Response should contain 'message'"
        assert "store" in data, "Response should contain 'store'"
        
        store = data["store"]
        assert store["store_url"] == unique_url, f"Store URL mismatch"
        assert "id" in store, "Store should have 'id'"
        assert "estimated_monthly_revenue" in store, "Store should have 'estimated_monthly_revenue'"
        assert "top_products" in store, "Store should have 'top_products'"
        assert "revenue_history" in store, "Store should have 'revenue_history'"
        
        print(f"✓ POST /api/stores/add creates tracked store: {store['store_name']}")
        print(f"  Estimated Monthly Revenue: ${store['estimated_monthly_revenue']:,}")
        
        # Return store ID for cleanup
        return store["id"]
    
    def test_get_tracked_stores_returns_list(self, admin_token):
        """GET /api/stores returns tracked stores list (requires auth)"""
        response = requests.get(
            f"{BASE_URL}/api/stores",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        
        assert "stores" in data, "Response should contain 'stores'"
        assert "total" in data, "Response should contain 'total'"
        assert "max_stores" in data, "Response should contain 'max_stores'"
        
        stores = data["stores"]
        assert isinstance(stores, list), "Stores should be a list"
        
        print(f"✓ GET /api/stores returns {len(stores)} tracked stores (max: {data['max_stores']})")
    
    def test_delete_store_removes_store(self, admin_token):
        """DELETE /api/stores/{id} removes a store (requires auth)"""
        # First create a store to delete
        unique_url = f"https://delete-test-{uuid.uuid4().hex[:8]}.myshopify.com"
        create_response = requests.post(
            f"{BASE_URL}/api/stores/add",
            headers={"Authorization": f"Bearer {admin_token}"},
            json={"store_url": unique_url, "name": "TEST_ToDelete"}
        )
        assert create_response.status_code == 200, f"Failed to create store: {create_response.text}"
        store_id = create_response.json()["store"]["id"]
        
        # Now delete it
        delete_response = requests.delete(
            f"{BASE_URL}/api/stores/{store_id}",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert delete_response.status_code == 200, f"Expected 200, got {delete_response.status_code}: {delete_response.text}"
        data = delete_response.json()
        assert "message" in data, "Response should contain 'message'"
        
        # Verify it's gone
        get_response = requests.get(
            f"{BASE_URL}/api/stores/{store_id}",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert get_response.status_code == 404, f"Store should be deleted, got {get_response.status_code}"
        
        print(f"✓ DELETE /api/stores/{store_id} removes store successfully")
    
    def test_delete_nonexistent_store_returns_404(self, admin_token):
        """DELETE /api/stores/{invalid_id} returns 404"""
        response = requests.delete(
            f"{BASE_URL}/api/stores/nonexistent-store-id-12345",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 404, f"Expected 404, got {response.status_code}: {response.text}"
        print("✓ DELETE /api/stores/{invalid_id} returns 404")
    
    def test_add_duplicate_store_returns_400(self, admin_token):
        """POST /api/stores/add with duplicate URL returns 400"""
        unique_url = f"https://duplicate-test-{uuid.uuid4().hex[:8]}.myshopify.com"
        
        # First add
        first_response = requests.post(
            f"{BASE_URL}/api/stores/add",
            headers={"Authorization": f"Bearer {admin_token}"},
            json={"store_url": unique_url, "name": "TEST_Duplicate1"}
        )
        assert first_response.status_code == 200, f"First add failed: {first_response.text}"
        
        # Second add (duplicate)
        second_response = requests.post(
            f"{BASE_URL}/api/stores/add",
            headers={"Authorization": f"Bearer {admin_token}"},
            json={"store_url": unique_url, "name": "TEST_Duplicate2"}
        )
        assert second_response.status_code == 400, f"Expected 400 for duplicate, got {second_response.status_code}"
        
        print("✓ POST /api/stores/add with duplicate URL returns 400")


# ============================================================================
# MARKETPLACE ENDPOINTS TESTS
# ============================================================================

class TestMarketplaceEndpointsNoAuth:
    """Test /api/marketplace endpoints without authentication - should return 401"""
    
    def test_briefs_returns_401_without_auth(self):
        """GET /api/marketplace/briefs should return 401 without auth"""
        response = requests.get(f"{BASE_URL}/api/marketplace/briefs")
        assert response.status_code == 401, f"Expected 401, got {response.status_code}: {response.text}"
        print("✓ GET /api/marketplace/briefs returns 401 without auth")
    
    def test_create_brief_returns_401_without_auth(self):
        """POST /api/marketplace/briefs should return 401 without auth"""
        response = requests.post(
            f"{BASE_URL}/api/marketplace/briefs",
            json={
                "product_name": "Test Product",
                "category": "Tech Gadgets",
                "description": "Test description",
                "budget_range": "$50-100",
                "commission_offered": 10.0,
                "content_type": "UGC Review"
            }
        )
        assert response.status_code == 401, f"Expected 401, got {response.status_code}: {response.text}"
        print("✓ POST /api/marketplace/briefs returns 401 without auth")
    
    def test_apply_returns_401_without_auth(self):
        """POST /api/marketplace/apply should return 401 without auth"""
        response = requests.post(
            f"{BASE_URL}/api/marketplace/apply",
            json={"brief_id": "some-brief-id", "message": "Test application"}
        )
        assert response.status_code == 401, f"Expected 401, got {response.status_code}: {response.text}"
        print("✓ POST /api/marketplace/apply returns 401 without auth")
    
    def test_stats_returns_401_without_auth(self):
        """GET /api/marketplace/stats should return 401 without auth"""
        response = requests.get(f"{BASE_URL}/api/marketplace/stats")
        assert response.status_code == 401, f"Expected 401, got {response.status_code}: {response.text}"
        print("✓ GET /api/marketplace/stats returns 401 without auth")


class TestMarketplaceEndpointsWithAuth:
    """Test /api/marketplace endpoints with admin authentication"""
    
    def test_create_brief_creates_new_brief(self, admin_token):
        """POST /api/marketplace/briefs creates a new brief (requires auth)"""
        brief_data = {
            "product_name": f"TEST_Product_{uuid.uuid4().hex[:6]}",
            "category": "Tech Gadgets",
            "description": "This is a test product brief for Phase 3 testing",
            "budget_range": "$100-300 per video",
            "commission_offered": 15.0,
            "content_type": "UGC Review",
            "requirements": "Must have 10k+ followers",
            "deadline": "2026-02-28"
        }
        
        response = requests.post(
            f"{BASE_URL}/api/marketplace/briefs",
            headers={"Authorization": f"Bearer {admin_token}"},
            json=brief_data
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        
        assert "message" in data, "Response should contain 'message'"
        assert "brief" in data, "Response should contain 'brief'"
        
        brief = data["brief"]
        assert brief["product_name"] == brief_data["product_name"], "Product name mismatch"
        assert brief["category"] == brief_data["category"], "Category mismatch"
        assert brief["commission_offered"] == brief_data["commission_offered"], "Commission mismatch"
        assert brief["status"] == "open", "Brief status should be 'open'"
        assert "id" in brief, "Brief should have 'id'"
        
        print(f"✓ POST /api/marketplace/briefs creates brief: {brief['product_name']}")
        print(f"  Commission: {brief['commission_offered']}%, Budget: {brief['budget_range']}")
        
        return brief["id"]
    
    def test_get_briefs_returns_list(self, admin_token):
        """GET /api/marketplace/briefs returns briefs list (requires auth)"""
        response = requests.get(
            f"{BASE_URL}/api/marketplace/briefs",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        
        assert "briefs" in data, "Response should contain 'briefs'"
        assert "total" in data, "Response should contain 'total'"
        
        briefs = data["briefs"]
        assert isinstance(briefs, list), "Briefs should be a list"
        
        print(f"✓ GET /api/marketplace/briefs returns {len(briefs)} briefs (total: {data['total']})")
    
    def test_apply_to_brief_submits_application(self, admin_token):
        """POST /api/marketplace/apply submits application (requires auth)"""
        # First create a brief to apply to
        brief_data = {
            "product_name": f"TEST_ApplyTarget_{uuid.uuid4().hex[:6]}",
            "category": "Beauty & Skincare",
            "description": "Test brief for application testing",
            "budget_range": "$50-150",
            "commission_offered": 12.0,
            "content_type": "Tutorial"
        }
        
        create_response = requests.post(
            f"{BASE_URL}/api/marketplace/briefs",
            headers={"Authorization": f"Bearer {admin_token}"},
            json=brief_data
        )
        assert create_response.status_code == 200, f"Failed to create brief: {create_response.text}"
        brief_id = create_response.json()["brief"]["id"]
        
        # Now apply to it
        application_data = {
            "brief_id": brief_id,
            "message": "I would love to create content for this product! I have experience in beauty tutorials.",
            "proposed_rate": 100.0,
            "portfolio_link": "https://tiktok.com/@testcreator"
        }
        
        apply_response = requests.post(
            f"{BASE_URL}/api/marketplace/apply",
            headers={"Authorization": f"Bearer {admin_token}"},
            json=application_data
        )
        assert apply_response.status_code == 200, f"Expected 200, got {apply_response.status_code}: {apply_response.text}"
        data = apply_response.json()
        
        assert "message" in data, "Response should contain 'message'"
        assert "application" in data, "Response should contain 'application'"
        
        application = data["application"]
        assert application["brief_id"] == brief_id, "Brief ID mismatch"
        assert application["status"] == "pending", "Application status should be 'pending'"
        assert "id" in application, "Application should have 'id'"
        
        print(f"✓ POST /api/marketplace/apply submits application to brief {brief_id}")
    
    def test_apply_to_nonexistent_brief_returns_404(self, admin_token):
        """POST /api/marketplace/apply to nonexistent brief returns 404"""
        response = requests.post(
            f"{BASE_URL}/api/marketplace/apply",
            headers={"Authorization": f"Bearer {admin_token}"},
            json={"brief_id": "nonexistent-brief-id-12345", "message": "Test"}
        )
        assert response.status_code == 404, f"Expected 404, got {response.status_code}: {response.text}"
        print("✓ POST /api/marketplace/apply to nonexistent brief returns 404")
    
    def test_get_marketplace_stats(self, admin_token):
        """GET /api/marketplace/stats returns marketplace statistics (requires auth)"""
        response = requests.get(
            f"{BASE_URL}/api/marketplace/stats",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        
        assert "total_briefs" in data, "Response should contain 'total_briefs'"
        assert "open_briefs" in data, "Response should contain 'open_briefs'"
        assert "total_applications" in data, "Response should contain 'total_applications'"
        assert "categories" in data, "Response should contain 'categories'"
        assert "content_types" in data, "Response should contain 'content_types'"
        
        print(f"✓ GET /api/marketplace/stats returns statistics")
        print(f"  Total Briefs: {data['total_briefs']}, Open: {data['open_briefs']}, Applications: {data['total_applications']}")
    
    def test_get_brief_detail(self, admin_token):
        """GET /api/marketplace/briefs/{id} returns brief with applications"""
        # First create a brief
        brief_data = {
            "product_name": f"TEST_DetailBrief_{uuid.uuid4().hex[:6]}",
            "category": "Health & Wellness",
            "description": "Test brief for detail endpoint",
            "budget_range": "$75-200",
            "commission_offered": 8.0,
            "content_type": "Before/After"
        }
        
        create_response = requests.post(
            f"{BASE_URL}/api/marketplace/briefs",
            headers={"Authorization": f"Bearer {admin_token}"},
            json=brief_data
        )
        assert create_response.status_code == 200, f"Failed to create brief: {create_response.text}"
        brief_id = create_response.json()["brief"]["id"]
        
        # Get detail
        detail_response = requests.get(
            f"{BASE_URL}/api/marketplace/briefs/{brief_id}",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert detail_response.status_code == 200, f"Expected 200, got {detail_response.status_code}: {detail_response.text}"
        data = detail_response.json()
        
        assert "brief" in data, "Response should contain 'brief'"
        assert "applications" in data, "Response should contain 'applications'"
        assert data["brief"]["id"] == brief_id, "Brief ID mismatch"
        
        print(f"✓ GET /api/marketplace/briefs/{brief_id} returns brief detail with applications")


# ============================================================================
# CLEANUP TEST DATA
# ============================================================================

class TestCleanup:
    """Clean up test data created during testing"""
    
    def test_cleanup_test_stores(self, admin_token):
        """Remove TEST_ prefixed stores"""
        response = requests.get(
            f"{BASE_URL}/api/stores",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        if response.status_code == 200:
            stores = response.json().get("stores", [])
            deleted = 0
            for store in stores:
                if store.get("store_name", "").startswith("TEST_"):
                    del_response = requests.delete(
                        f"{BASE_URL}/api/stores/{store['id']}",
                        headers={"Authorization": f"Bearer {admin_token}"}
                    )
                    if del_response.status_code == 200:
                        deleted += 1
            print(f"✓ Cleaned up {deleted} test stores")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
