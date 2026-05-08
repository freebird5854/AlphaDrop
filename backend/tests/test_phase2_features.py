"""
Test Phase 2 Features: AI Tools (Script Generator, Sentiment Analysis) and Ad Creative Library
Tests for ALPHA DROP iteration 7 features.
"""
import pytest
import requests
import os
import time

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')
ADMIN_EMAIL = "admin@alphadrop.com"
ADMIN_PASSWORD = "AlphaDr0p!2026"


class TestAdminAuth:
    """Admin authentication tests"""
    
    def test_admin_login_success(self):
        """POST /api/admin/login with correct credentials returns JWT token"""
        response = requests.post(
            f"{BASE_URL}/api/admin/login",
            json={"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD}
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        assert "token" in data, "Response should contain token"
        assert "email" in data, "Response should contain email"
        assert data["email"] == ADMIN_EMAIL
        print(f"✓ Admin login successful, token received")
        return data["token"]


class TestAdLibraryEndpoints:
    """Ad Creative Library endpoint tests"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Get admin token for authenticated requests"""
        response = requests.post(
            f"{BASE_URL}/api/admin/login",
            json={"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD}
        )
        assert response.status_code == 200
        self.token = response.json()["token"]
        self.headers = {"Authorization": f"Bearer {self.token}"}
    
    def test_get_ads_returns_401_without_auth(self):
        """GET /api/ads returns 401 without authentication"""
        response = requests.get(f"{BASE_URL}/api/ads")
        assert response.status_code == 401, f"Expected 401, got {response.status_code}"
        print("✓ GET /api/ads returns 401 without auth")
    
    def test_get_ads_with_auth(self):
        """GET /api/ads returns ad library data with ads array and format_stats"""
        response = requests.get(f"{BASE_URL}/api/ads", headers=self.headers)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        
        # Verify response structure
        assert "ads" in data, "Response should contain 'ads' array"
        assert "format_stats" in data, "Response should contain 'format_stats'"
        assert "total" in data, "Response should contain 'total'"
        assert "formats" in data, "Response should contain 'formats'"
        
        # Verify ads array structure
        assert isinstance(data["ads"], list), "ads should be a list"
        if len(data["ads"]) > 0:
            ad = data["ads"][0]
            assert "id" in ad, "Ad should have id"
            assert "product_name" in ad, "Ad should have product_name"
            assert "format" in ad, "Ad should have format"
            assert "hook_text" in ad, "Ad should have hook_text"
            assert "views" in ad, "Ad should have views"
        
        print(f"✓ GET /api/ads returns {len(data['ads'])} ads with format_stats")
    
    def test_get_ads_with_limit(self):
        """GET /api/ads?limit=5 returns max 5 ads"""
        response = requests.get(f"{BASE_URL}/api/ads?limit=5", headers=self.headers)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        data = response.json()
        
        assert len(data["ads"]) <= 5, f"Expected max 5 ads, got {len(data['ads'])}"
        print(f"✓ GET /api/ads?limit=5 returns {len(data['ads'])} ads (max 5)")
    
    def test_get_top_hooks_returns_401_without_auth(self):
        """GET /api/ads/top-hooks returns 401 without authentication"""
        response = requests.get(f"{BASE_URL}/api/ads/top-hooks")
        assert response.status_code == 401, f"Expected 401, got {response.status_code}"
        print("✓ GET /api/ads/top-hooks returns 401 without auth")
    
    def test_get_top_hooks_with_auth(self):
        """GET /api/ads/top-hooks returns ranked hooks by views"""
        response = requests.get(f"{BASE_URL}/api/ads/top-hooks", headers=self.headers)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        
        assert "top_hooks" in data, "Response should contain 'top_hooks'"
        assert isinstance(data["top_hooks"], list), "top_hooks should be a list"
        
        if len(data["top_hooks"]) > 0:
            hook = data["top_hooks"][0]
            assert "hook" in hook, "Hook should have 'hook' text"
            assert "total_views" in hook, "Hook should have 'total_views'"
            assert "avg_ctr" in hook, "Hook should have 'avg_ctr'"
            assert "times_used" in hook, "Hook should have 'times_used'"
        
        print(f"✓ GET /api/ads/top-hooks returns {len(data['top_hooks'])} hooks")
    
    def test_get_duplication_alerts_returns_401_without_auth(self):
        """GET /api/ads/duplication-alerts returns 401 without authentication"""
        response = requests.get(f"{BASE_URL}/api/ads/duplication-alerts")
        assert response.status_code == 401, f"Expected 401, got {response.status_code}"
        print("✓ GET /api/ads/duplication-alerts returns 401 without auth")
    
    def test_get_duplication_alerts_with_auth(self):
        """GET /api/ads/duplication-alerts returns products with high ad duplication"""
        response = requests.get(f"{BASE_URL}/api/ads/duplication-alerts", headers=self.headers)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        
        assert "duplication_alerts" in data, "Response should contain 'duplication_alerts'"
        assert isinstance(data["duplication_alerts"], list), "duplication_alerts should be a list"
        
        if len(data["duplication_alerts"]) > 0:
            alert = data["duplication_alerts"][0]
            assert "product_id" in alert, "Alert should have 'product_id'"
            assert "product_name" in alert, "Alert should have 'product_name'"
            assert "total_ads" in alert, "Alert should have 'total_ads'"
            assert "unique_advertisers" in alert, "Alert should have 'unique_advertisers'"
            assert "saturation_signal" in alert, "Alert should have 'saturation_signal'"
        
        print(f"✓ GET /api/ads/duplication-alerts returns {len(data['duplication_alerts'])} alerts")


class TestAIToolsEndpoints:
    """AI Script Generator and Sentiment Analysis endpoint tests"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Get admin token and a product ID for testing"""
        # Get admin token
        response = requests.post(
            f"{BASE_URL}/api/admin/login",
            json={"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD}
        )
        assert response.status_code == 200
        self.token = response.json()["token"]
        self.headers = {"Authorization": f"Bearer {self.token}"}
        
        # Get a product ID for testing
        response = requests.get(f"{BASE_URL}/api/products?limit=1", headers=self.headers)
        assert response.status_code == 200
        products = response.json()
        assert len(products) > 0, "Need at least one product for testing"
        self.product_id = products[0]["id"]
        self.product_name = products[0]["name"]
        print(f"Using product: {self.product_name} ({self.product_id})")
    
    def test_generate_scripts_returns_401_without_auth(self):
        """POST /api/ai/generate-scripts returns 401 without authentication"""
        response = requests.post(f"{BASE_URL}/api/ai/generate-scripts?product_id=test123")
        assert response.status_code == 401, f"Expected 401, got {response.status_code}"
        print("✓ POST /api/ai/generate-scripts returns 401 without auth")
    
    def test_generate_scripts_returns_404_for_invalid_product(self):
        """POST /api/ai/generate-scripts returns 404 for non-existent product"""
        response = requests.post(
            f"{BASE_URL}/api/ai/generate-scripts?product_id=invalid-product-id",
            headers=self.headers
        )
        assert response.status_code == 404, f"Expected 404, got {response.status_code}"
        print("✓ POST /api/ai/generate-scripts returns 404 for invalid product")
    
    def test_generate_scripts_with_valid_product(self):
        """POST /api/ai/generate-scripts?product_id={id} generates scripts (requires auth)"""
        response = requests.post(
            f"{BASE_URL}/api/ai/generate-scripts?product_id={self.product_id}",
            headers=self.headers,
            timeout=60  # AI calls may take time
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        
        # Verify response structure
        assert "product_id" in data, "Response should contain 'product_id'"
        assert "product_name" in data, "Response should contain 'product_name'"
        assert "scripts" in data, "Response should contain 'scripts'"
        assert data["product_id"] == self.product_id
        
        # Verify scripts array
        assert isinstance(data["scripts"], list), "scripts should be a list"
        assert len(data["scripts"]) > 0, "Should have at least one script"
        
        # Check script structure (may vary based on LLM response)
        script = data["scripts"][0]
        # Scripts should have some content
        assert len(str(script)) > 10, "Script should have content"
        
        print(f"✓ POST /api/ai/generate-scripts generated {len(data['scripts'])} scripts for {self.product_name}")
    
    def test_analyze_sentiment_returns_401_without_auth(self):
        """POST /api/ai/analyze-sentiment returns 401 without authentication"""
        response = requests.post(f"{BASE_URL}/api/ai/analyze-sentiment?product_id=test123")
        assert response.status_code == 401, f"Expected 401, got {response.status_code}"
        print("✓ POST /api/ai/analyze-sentiment returns 401 without auth")
    
    def test_analyze_sentiment_returns_404_for_invalid_product(self):
        """POST /api/ai/analyze-sentiment returns 404 for non-existent product"""
        response = requests.post(
            f"{BASE_URL}/api/ai/analyze-sentiment?product_id=invalid-product-id",
            headers=self.headers
        )
        assert response.status_code == 404, f"Expected 404, got {response.status_code}"
        print("✓ POST /api/ai/analyze-sentiment returns 404 for invalid product")
    
    def test_analyze_sentiment_with_valid_product(self):
        """POST /api/ai/analyze-sentiment?product_id={id} returns sentiment scores"""
        response = requests.post(
            f"{BASE_URL}/api/ai/analyze-sentiment?product_id={self.product_id}",
            headers=self.headers,
            timeout=60  # AI calls may take time
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        
        # Verify response structure
        assert "product_id" in data, "Response should contain 'product_id'"
        assert "product_name" in data, "Response should contain 'product_name'"
        assert "analysis" in data, "Response should contain 'analysis'"
        assert "comments_analyzed" in data, "Response should contain 'comments_analyzed'"
        assert data["product_id"] == self.product_id
        
        # Verify analysis structure
        analysis = data["analysis"]
        assert isinstance(analysis, dict), "analysis should be a dict"
        
        # Check for expected sentiment fields (may vary based on LLM response)
        expected_fields = ["buyer_intent_score", "quality_perception_score", "recommendation"]
        for field in expected_fields:
            if field in analysis:
                print(f"  - {field}: {analysis[field]}")
        
        print(f"✓ POST /api/ai/analyze-sentiment returned analysis for {self.product_name}")


class TestCachedAIResults:
    """Test cached AI results endpoints"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Get admin token"""
        response = requests.post(
            f"{BASE_URL}/api/admin/login",
            json={"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD}
        )
        assert response.status_code == 200
        self.token = response.json()["token"]
        self.headers = {"Authorization": f"Bearer {self.token}"}
        
        # Get a product ID
        response = requests.get(f"{BASE_URL}/api/products?limit=1", headers=self.headers)
        assert response.status_code == 200
        products = response.json()
        self.product_id = products[0]["id"] if products else None
    
    def test_get_cached_scripts_returns_401_without_auth(self):
        """GET /api/ai/scripts/{product_id} returns 401 without auth"""
        response = requests.get(f"{BASE_URL}/api/ai/scripts/test123")
        assert response.status_code == 401, f"Expected 401, got {response.status_code}"
        print("✓ GET /api/ai/scripts/{product_id} returns 401 without auth")
    
    def test_get_cached_sentiment_returns_401_without_auth(self):
        """GET /api/ai/sentiment/{product_id} returns 401 without auth"""
        response = requests.get(f"{BASE_URL}/api/ai/sentiment/test123")
        assert response.status_code == 401, f"Expected 401, got {response.status_code}"
        print("✓ GET /api/ai/sentiment/{product_id} returns 401 without auth")


class TestCommandBarIntegration:
    """Test that CommandBar component is properly integrated"""
    
    def test_frontend_loads(self):
        """Frontend should load without errors"""
        response = requests.get(BASE_URL)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        print("✓ Frontend loads successfully")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
