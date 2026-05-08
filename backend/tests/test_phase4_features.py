"""
Phase 4 Backend Tests - Creator Portal, Push Notifications, Store Refresh
Tests: Creator registration/login, push notification endpoints, store refresh with Shopify API
"""
import pytest
import requests
import os
import uuid

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Test credentials
ADMIN_EMAIL = "admin@alphadrop.com"
ADMIN_PASSWORD = "AlphaDr0p!2026"

# Test creator data - unique per run
TEST_CREATOR_EMAIL = f"testcreator_{uuid.uuid4().hex[:8]}@test.com"
TEST_CREATOR_PASSWORD = "TestPass123!"
TEST_CREATOR_HANDLE = f"testhandle_{uuid.uuid4().hex[:8]}"


@pytest.fixture(scope="module")
def api_client():
    """Shared requests session"""
    session = requests.Session()
    session.headers.update({"Content-Type": "application/json"})
    return session


@pytest.fixture(scope="module")
def admin_token(api_client):
    """Get admin JWT token"""
    response = api_client.post(f"{BASE_URL}/api/admin/login", json={
        "email": ADMIN_EMAIL,
        "password": ADMIN_PASSWORD
    })
    if response.status_code == 200:
        return response.json().get("token")
    pytest.skip("Admin authentication failed - skipping authenticated tests")


@pytest.fixture(scope="module")
def admin_client(api_client, admin_token):
    """Session with admin auth header"""
    api_client.headers.update({"Authorization": f"Bearer {admin_token}"})
    return api_client


# ============ CREATOR REGISTRATION TESTS ============

class TestCreatorRegistration:
    """Creator self-registration portal tests"""
    
    def test_creator_register_success(self, api_client):
        """POST /api/creators/register creates a creator account (public endpoint)"""
        response = api_client.post(f"{BASE_URL}/api/creators/register", json={
            "email": TEST_CREATOR_EMAIL,
            "password": TEST_CREATOR_PASSWORD,
            "name": "Test Creator",
            "handle": TEST_CREATOR_HANDLE,
            "niche": "Beauty",
            "followers": 50000,
            "engagement_rate": 5.5
        })
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        assert "creator" in data
        assert data["creator"]["email"] == TEST_CREATOR_EMAIL.lower()
        assert data["creator"]["handle"] == TEST_CREATOR_HANDLE.lower()
        assert data["creator"]["niche"] == "Beauty"
        assert "password_hash" not in data["creator"]  # Should not expose password hash
        print(f"✓ Creator registered: {TEST_CREATOR_EMAIL}")
    
    def test_creator_register_duplicate_email(self, api_client):
        """POST /api/creators/register with duplicate email returns 400"""
        response = api_client.post(f"{BASE_URL}/api/creators/register", json={
            "email": TEST_CREATOR_EMAIL,  # Same email as above
            "password": "AnotherPass123!",
            "name": "Duplicate Creator",
            "handle": f"duplicate_{uuid.uuid4().hex[:8]}",
            "niche": "Fashion"
        })
        
        assert response.status_code == 400, f"Expected 400, got {response.status_code}: {response.text}"
        data = response.json()
        assert "already registered" in data.get("detail", "").lower()
        print("✓ Duplicate email correctly rejected")
    
    def test_creator_register_duplicate_handle(self, api_client):
        """POST /api/creators/register with duplicate handle returns 400"""
        response = api_client.post(f"{BASE_URL}/api/creators/register", json={
            "email": f"unique_{uuid.uuid4().hex[:8]}@test.com",
            "password": "AnotherPass123!",
            "name": "Another Creator",
            "handle": TEST_CREATOR_HANDLE,  # Same handle as above
            "niche": "Fashion"
        })
        
        assert response.status_code == 400, f"Expected 400, got {response.status_code}: {response.text}"
        data = response.json()
        assert "handle" in data.get("detail", "").lower() or "taken" in data.get("detail", "").lower()
        print("✓ Duplicate handle correctly rejected")


# ============ CREATOR LOGIN TESTS ============

class TestCreatorLogin:
    """Creator login tests"""
    
    def test_creator_login_success(self, api_client):
        """POST /api/creators/login with correct credentials returns token"""
        response = api_client.post(f"{BASE_URL}/api/creators/login", json={
            "email": TEST_CREATOR_EMAIL,
            "password": TEST_CREATOR_PASSWORD
        })
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        assert "token" in data
        assert "creator" in data
        assert data["creator"]["email"] == TEST_CREATOR_EMAIL.lower()
        assert len(data["token"]) > 0
        print(f"✓ Creator login successful, token received")
    
    def test_creator_login_wrong_password(self, api_client):
        """POST /api/creators/login with wrong password returns 401"""
        response = api_client.post(f"{BASE_URL}/api/creators/login", json={
            "email": TEST_CREATOR_EMAIL,
            "password": "WrongPassword123!"
        })
        
        assert response.status_code == 401, f"Expected 401, got {response.status_code}: {response.text}"
        data = response.json()
        assert "invalid" in data.get("detail", "").lower() or "credentials" in data.get("detail", "").lower()
        print("✓ Wrong password correctly rejected with 401")
    
    def test_creator_login_nonexistent_email(self, api_client):
        """POST /api/creators/login with nonexistent email returns 401"""
        response = api_client.post(f"{BASE_URL}/api/creators/login", json={
            "email": "nonexistent@test.com",
            "password": "SomePassword123!"
        })
        
        assert response.status_code == 401, f"Expected 401, got {response.status_code}: {response.text}"
        print("✓ Nonexistent email correctly rejected with 401")


# ============ CREATOR BROWSE/PROFILE TESTS ============

class TestCreatorBrowse:
    """Creator browse and profile tests (public endpoints)"""
    
    def test_browse_creators(self, api_client):
        """GET /api/creators/browse returns registered creators (public)"""
        response = api_client.get(f"{BASE_URL}/api/creators/browse")
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        assert "creators" in data
        assert "total" in data
        assert isinstance(data["creators"], list)
        print(f"✓ Browse creators returned {data['total']} creators")
    
    def test_browse_creators_with_filter(self, api_client):
        """GET /api/creators/browse with niche filter"""
        response = api_client.get(f"{BASE_URL}/api/creators/browse?niche=Beauty")
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        assert "creators" in data
        # All returned creators should have Beauty niche
        for creator in data["creators"]:
            assert creator.get("niche") == "Beauty"
        print(f"✓ Browse with niche filter returned {len(data['creators'])} Beauty creators")
    
    def test_get_creator_profile(self, api_client):
        """GET /api/creators/profile/{id} returns creator profile (public)"""
        # First get a creator ID from browse
        browse_response = api_client.get(f"{BASE_URL}/api/creators/browse?limit=1")
        assert browse_response.status_code == 200
        creators = browse_response.json().get("creators", [])
        
        if not creators:
            pytest.skip("No creators found to test profile endpoint")
        
        creator_id = creators[0]["id"]
        response = api_client.get(f"{BASE_URL}/api/creators/profile/{creator_id}")
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        assert data["id"] == creator_id
        assert "email" in data
        assert "password_hash" not in data  # Should not expose password hash
        print(f"✓ Creator profile retrieved: {data.get('name', 'Unknown')}")
    
    def test_get_creator_profile_not_found(self, api_client):
        """GET /api/creators/profile/{invalid_id} returns 404"""
        response = api_client.get(f"{BASE_URL}/api/creators/profile/nonexistent-id-12345")
        
        assert response.status_code == 404, f"Expected 404, got {response.status_code}: {response.text}"
        print("✓ Nonexistent creator profile returns 404")


# ============ PUSH NOTIFICATION TESTS ============

class TestPushNotifications:
    """Push notification endpoint tests"""
    
    def test_push_register_without_auth(self, api_client):
        """POST /api/notifications/push/register returns 401 without auth"""
        # Remove auth header if present
        client = requests.Session()
        client.headers.update({"Content-Type": "application/json"})
        
        response = client.post(f"{BASE_URL}/api/notifications/push/register", json={
            "push_token": "ExponentPushToken[test123]",
            "platform": "ios"
        })
        
        assert response.status_code == 401, f"Expected 401, got {response.status_code}: {response.text}"
        print("✓ Push register correctly requires auth (401)")
    
    def test_push_register_with_auth(self, admin_client):
        """POST /api/notifications/push/register registers token (with admin auth)"""
        response = admin_client.post(f"{BASE_URL}/api/notifications/push/register", json={
            "push_token": f"ExponentPushToken[test_{uuid.uuid4().hex[:8]}]",
            "platform": "ios",
            "device_name": "Test iPhone"
        })
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        assert "message" in data
        assert data.get("platform") == "ios"
        print("✓ Push token registered successfully")
    
    def test_push_send_test_with_auth(self, admin_client):
        """POST /api/notifications/push/send-test sends test push (with admin auth)"""
        response = admin_client.post(f"{BASE_URL}/api/notifications/push/send-test")
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        assert "message" in data
        print(f"✓ Test push sent: {data.get('message')}")
    
    def test_push_broadcast_without_auth(self, api_client):
        """POST /api/notifications/push/broadcast returns 401 without auth or cron key"""
        # Use fresh client without auth
        client = requests.Session()
        client.headers.update({"Content-Type": "application/json"})
        
        response = client.post(f"{BASE_URL}/api/notifications/push/broadcast", json={
            "title": "Test Broadcast",
            "body": "This should fail"
        })
        
        assert response.status_code == 401, f"Expected 401, got {response.status_code}: {response.text}"
        print("✓ Broadcast correctly requires auth (401)")
    
    def test_push_broadcast_with_cron_key(self, api_client):
        """POST /api/notifications/push/broadcast with cron key succeeds"""
        response = api_client.post(
            f"{BASE_URL}/api/notifications/push/broadcast?api_key=alpha-drop-cron-2024",
            json={
                "title": "Test Broadcast",
                "body": "Test broadcast message"
            }
        )
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        assert "message" in data
        print(f"✓ Broadcast with cron key: {data.get('message')}")


# ============ STORE REFRESH TESTS ============

class TestStoreRefresh:
    """Store refresh endpoint tests (Shopify API integration)"""
    
    def test_store_refresh_without_auth(self, api_client):
        """POST /api/stores/{id}/refresh returns 401 without auth"""
        client = requests.Session()
        client.headers.update({"Content-Type": "application/json"})
        
        response = client.post(f"{BASE_URL}/api/stores/test-store-id/refresh")
        
        assert response.status_code == 401, f"Expected 401, got {response.status_code}: {response.text}"
        print("✓ Store refresh correctly requires auth (401)")
    
    def test_store_refresh_endpoint_exists(self, admin_client):
        """POST /api/stores/{id}/refresh endpoint exists (requires auth)"""
        # First add a test store
        add_response = admin_client.post(f"{BASE_URL}/api/stores/add", json={
            "store_url": "https://example-store.myshopify.com",
            "name": "Test Store for Refresh"
        })
        
        if add_response.status_code == 200:
            store_id = add_response.json().get("store", {}).get("id")
            
            # Try to refresh
            response = admin_client.post(f"{BASE_URL}/api/stores/{store_id}/refresh")
            
            # Should return 200 with either real data or simulated message
            assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
            data = response.json()
            assert "message" in data
            assert "source" in data  # Should indicate shopify_api or simulated
            print(f"✓ Store refresh: {data.get('message')} (source: {data.get('source')})")
            
            # Cleanup - remove test store
            admin_client.delete(f"{BASE_URL}/api/stores/{store_id}")
        elif add_response.status_code == 400 and "already tracked" in add_response.text.lower():
            # Store already exists, try to find it
            stores_response = admin_client.get(f"{BASE_URL}/api/stores")
            if stores_response.status_code == 200:
                stores = stores_response.json().get("stores", [])
                for store in stores:
                    if "example-store" in store.get("store_url", ""):
                        store_id = store["id"]
                        response = admin_client.post(f"{BASE_URL}/api/stores/{store_id}/refresh")
                        assert response.status_code == 200
                        print(f"✓ Store refresh on existing store: {response.json().get('message')}")
                        break
        else:
            pytest.skip(f"Could not add test store: {add_response.status_code}")
    
    def test_store_refresh_not_found(self, admin_client):
        """POST /api/stores/{invalid_id}/refresh returns 404"""
        response = admin_client.post(f"{BASE_URL}/api/stores/nonexistent-store-id/refresh")
        
        assert response.status_code == 404, f"Expected 404, got {response.status_code}: {response.text}"
        print("✓ Refresh nonexistent store returns 404")


# ============ SUMMARY ============

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
