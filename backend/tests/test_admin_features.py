"""
Test suite for ALPHA DROP Admin Panel, CSV Export, and Updated Pricing
Tests: Admin login, dashboard, subscriber management, CSV export, pricing updates
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Admin credentials from test_credentials.md
ADMIN_EMAIL = "admin@alphadrop.com"
ADMIN_PASSWORD = "AlphaDr0p!2026"


class TestAdminLogin:
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
        assert data["email"] == ADMIN_EMAIL.lower(), f"Email mismatch: {data.get('email')}"
        assert len(data["token"]) > 0, "Token should not be empty"
        
    def test_admin_login_wrong_password(self):
        """POST /api/admin/login with wrong password returns 401"""
        response = requests.post(
            f"{BASE_URL}/api/admin/login",
            json={"email": ADMIN_EMAIL, "password": "wrongpassword"}
        )
        assert response.status_code == 401, f"Expected 401, got {response.status_code}"
        
    def test_admin_login_wrong_email(self):
        """POST /api/admin/login with wrong email returns 401"""
        response = requests.post(
            f"{BASE_URL}/api/admin/login",
            json={"email": "wrong@email.com", "password": ADMIN_PASSWORD}
        )
        assert response.status_code == 401, f"Expected 401, got {response.status_code}"
        
    def test_admin_login_missing_fields(self):
        """POST /api/admin/login with missing fields returns 422"""
        response = requests.post(
            f"{BASE_URL}/api/admin/login",
            json={"email": ADMIN_EMAIL}  # Missing password
        )
        assert response.status_code == 422, f"Expected 422, got {response.status_code}"


class TestAdminDashboard:
    """Admin dashboard and protected endpoints tests"""
    
    @pytest.fixture
    def admin_token(self):
        """Get admin JWT token"""
        response = requests.post(
            f"{BASE_URL}/api/admin/login",
            json={"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD}
        )
        if response.status_code == 200:
            return response.json()["token"]
        pytest.skip("Admin login failed")
        
    def test_admin_me_with_token(self, admin_token):
        """GET /api/admin/me with valid token returns admin info"""
        response = requests.get(
            f"{BASE_URL}/api/admin/me",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        assert data["email"] == ADMIN_EMAIL.lower()
        assert data["role"] == "admin"
        
    def test_admin_me_without_token(self):
        """GET /api/admin/me without token returns 401"""
        response = requests.get(f"{BASE_URL}/api/admin/me")
        assert response.status_code == 401, f"Expected 401, got {response.status_code}"
        
    def test_admin_dashboard_with_token(self, admin_token):
        """GET /api/admin/dashboard returns stats with valid token"""
        response = requests.get(
            f"{BASE_URL}/api/admin/dashboard",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        
        # Verify dashboard structure
        assert "products" in data, "Dashboard should have products stats"
        assert "users" in data, "Dashboard should have users stats"
        assert "revenue" in data, "Dashboard should have revenue stats"
        
        # Verify products breakdown
        assert "total" in data["products"]
        assert "explosive" in data["products"]
        assert "rising" in data["products"]
        assert "early_signal" in data["products"]
        
        # Verify users breakdown
        assert "total" in data["users"]
        assert "active_subscribers" in data["users"]
        
        # Verify revenue breakdown
        assert "total" in data["revenue"]
        
    def test_admin_dashboard_without_token(self):
        """GET /api/admin/dashboard without token returns 401"""
        response = requests.get(f"{BASE_URL}/api/admin/dashboard")
        assert response.status_code == 401, f"Expected 401, got {response.status_code}"


class TestAdminSubscriberManagement:
    """Admin subscriber management tests"""
    
    @pytest.fixture
    def admin_token(self):
        """Get admin JWT token"""
        response = requests.post(
            f"{BASE_URL}/api/admin/login",
            json={"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD}
        )
        if response.status_code == 200:
            return response.json()["token"]
        pytest.skip("Admin login failed")
        
    def test_admin_subscribers_list(self, admin_token):
        """GET /api/admin/subscribers returns subscriber list"""
        response = requests.get(
            f"{BASE_URL}/api/admin/subscribers",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        assert "subscribers" in data, "Response should have subscribers key"
        assert isinstance(data["subscribers"], list), "Subscribers should be a list"
        
    def test_admin_users_list(self, admin_token):
        """GET /api/admin/users returns user list"""
        response = requests.get(
            f"{BASE_URL}/api/admin/users",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        assert "users" in data, "Response should have users key"
        assert isinstance(data["users"], list), "Users should be a list"
        
    def test_admin_payments_list(self, admin_token):
        """GET /api/admin/payments returns payment list"""
        response = requests.get(
            f"{BASE_URL}/api/admin/payments",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        assert "payments" in data, "Response should have payments key"
        assert isinstance(data["payments"], list), "Payments should be a list"
        
    def test_admin_grant_subscription(self, admin_token):
        """POST /api/admin/subscribers/{email}/activate grants subscription"""
        test_email = "TEST_grantuser@example.com"
        response = requests.post(
            f"{BASE_URL}/api/admin/subscribers/{test_email}/activate?plan_id=hunter",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        assert "message" in data, "Response should have message"
        
        # Verify subscription was created
        check_response = requests.get(
            f"{BASE_URL}/api/subscription/check?email={test_email}"
        )
        assert check_response.status_code == 200, "Subscription should exist after grant"
        sub_data = check_response.json()
        assert sub_data["status"] == "active"
        assert sub_data["plan_id"] == "hunter"
        
    def test_admin_deactivate_subscription(self, admin_token):
        """POST /api/admin/subscribers/{email}/deactivate deactivates subscription"""
        test_email = "TEST_deactivateuser@example.com"
        
        # First grant a subscription
        requests.post(
            f"{BASE_URL}/api/admin/subscribers/{test_email}/activate?plan_id=scout",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        
        # Then deactivate it
        response = requests.post(
            f"{BASE_URL}/api/admin/subscribers/{test_email}/deactivate",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        # Verify subscription is no longer active
        check_response = requests.get(
            f"{BASE_URL}/api/subscription/check?email={test_email}"
        )
        assert check_response.status_code == 404, "Subscription should not be active after deactivation"


class TestCSVExport:
    """CSV export endpoint tests"""
    
    def test_export_products_without_auth(self):
        """GET /api/export/products without auth returns 401"""
        response = requests.get(f"{BASE_URL}/api/export/products")
        assert response.status_code == 401, f"Expected 401, got {response.status_code}"
        
    def test_export_watchlist_without_auth(self):
        """GET /api/export/watchlist/{user_id} without auth returns 401"""
        response = requests.get(f"{BASE_URL}/api/export/watchlist/test_user")
        assert response.status_code == 401, f"Expected 401, got {response.status_code}"


class TestUpdatedPricing:
    """Updated pricing tests - $79/$199/$499 + $99 affiliate add-on"""
    
    def test_plans_endpoint_returns_updated_prices(self):
        """GET /api/plans returns updated prices"""
        response = requests.get(f"{BASE_URL}/api/plans")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        data = response.json()
        
        assert "plans" in data, "Response should have plans key"
        plans = data["plans"]
        
        # Verify Scout plan - $79
        assert "scout" in plans, "Scout plan should exist"
        assert plans["scout"]["price"] == 79.00, f"Scout price should be $79, got {plans['scout']['price']}"
        assert plans["scout"]["name"] == "Scout"
        
        # Verify Hunter plan - $199
        assert "hunter" in plans, "Hunter plan should exist"
        assert plans["hunter"]["price"] == 199.00, f"Hunter price should be $199, got {plans['hunter']['price']}"
        assert plans["hunter"]["name"] == "Hunter"
        
        # Verify Predator plan - $499
        assert "predator" in plans, "Predator plan should exist"
        assert plans["predator"]["price"] == 499.00, f"Predator price should be $499, got {plans['predator']['price']}"
        assert plans["predator"]["name"] == "Predator"
        
        # Verify Affiliate Pro add-on - $99
        assert "affiliate_pro" in plans, "Affiliate Pro add-on should exist"
        assert plans["affiliate_pro"]["price"] == 99.00, f"Affiliate Pro price should be $99, got {plans['affiliate_pro']['price']}"
        assert plans["affiliate_pro"]["is_addon"] == True, "Affiliate Pro should be marked as add-on"


class TestPWAManifest:
    """PWA manifest accessibility test"""
    
    def test_manifest_accessible(self):
        """GET /manifest.json is accessible"""
        # The manifest is served by the frontend, not the API
        # We test the frontend URL
        frontend_url = BASE_URL.replace('/api', '')
        response = requests.get(f"{frontend_url}/manifest.json")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        data = response.json()
        
        # Verify manifest structure
        assert "name" in data, "Manifest should have name"
        assert "short_name" in data, "Manifest should have short_name"
        assert "start_url" in data, "Manifest should have start_url"
        assert "display" in data, "Manifest should have display"
        assert "icons" in data, "Manifest should have icons"


class TestAdminLogout:
    """Admin logout test"""
    
    def test_admin_logout(self):
        """POST /api/admin/logout clears admin session"""
        # First login
        login_response = requests.post(
            f"{BASE_URL}/api/admin/login",
            json={"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD}
        )
        assert login_response.status_code == 200
        
        # Then logout
        response = requests.post(f"{BASE_URL}/api/admin/logout")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        data = response.json()
        assert "message" in data


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
