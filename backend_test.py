#!/usr/bin/env python3

import requests
import sys
import json
from datetime import datetime

class AlphaDropAPITester:
    def __init__(self, base_url="https://viral-product-scout-1.preview.emergentagent.com"):
        self.base_url = base_url
        self.api_base = f"{base_url}/api"
        self.tests_run = 0
        self.tests_passed = 0
        self.test_results = []

    def log_test(self, name, success, details=""):
        """Log test result"""
        self.tests_run += 1
        if success:
            self.tests_passed += 1
        
        result = {
            "test": name,
            "success": success,
            "details": details,
            "timestamp": datetime.now().isoformat()
        }
        self.test_results.append(result)
        
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} - {name}")
        if details:
            print(f"    {details}")

    def test_api_root(self):
        """Test API root endpoint"""
        try:
            response = requests.get(f"{self.api_base}/", timeout=10)
            success = response.status_code == 200
            
            if success:
                data = response.json()
                details = f"Status: {response.status_code}, Message: {data.get('message', 'N/A')}"
            else:
                details = f"Status: {response.status_code}"
                
            self.log_test("API Root Endpoint", success, details)
            return success
        except Exception as e:
            self.log_test("API Root Endpoint", False, f"Error: {str(e)}")
            return False

    def test_get_products(self):
        """Test get products endpoint"""
        try:
            response = requests.get(f"{self.api_base}/products", timeout=15)
            success = response.status_code == 200
            
            if success:
                data = response.json()
                product_count = len(data)
                details = f"Status: {response.status_code}, Products returned: {product_count}"
                
                # Validate product structure
                if product_count > 0:
                    product = data[0]
                    required_fields = ['id', 'name', 'alpha_score', 'status', 'price', 'category']
                    missing_fields = [field for field in required_fields if field not in product]
                    if missing_fields:
                        details += f", Missing fields: {missing_fields}"
                        success = False
            else:
                details = f"Status: {response.status_code}"
                
            self.log_test("Get Products", success, details)
            return success, data if success else []
        except Exception as e:
            self.log_test("Get Products", False, f"Error: {str(e)}")
            return False, []

    def test_dashboard_products(self):
        """Test dashboard products endpoint"""
        try:
            response = requests.get(f"{self.api_base}/products/dashboard", timeout=15)
            success = response.status_code == 200
            
            if success:
                data = response.json()
                sections = ['explosive', 'rising', 'early_signals']
                missing_sections = [section for section in sections if section not in data]
                
                if missing_sections:
                    success = False
                    details = f"Missing sections: {missing_sections}"
                else:
                    explosive_count = len(data.get('explosive', []))
                    rising_count = len(data.get('rising', []))
                    early_count = len(data.get('early_signals', []))
                    details = f"Explosive: {explosive_count}, Rising: {rising_count}, Early: {early_count}"
            else:
                details = f"Status: {response.status_code}"
                
            self.log_test("Dashboard Products", success, details)
            return success
        except Exception as e:
            self.log_test("Dashboard Products", False, f"Error: {str(e)}")
            return False

    def test_get_stats(self):
        """Test dashboard stats endpoint"""
        try:
            response = requests.get(f"{self.api_base}/stats", timeout=10)
            success = response.status_code == 200
            
            if success:
                data = response.json()
                required_fields = ['total_products_tracked', 'explosive_count', 'rising_count', 'early_signal_count']
                missing_fields = [field for field in required_fields if field not in data]
                
                if missing_fields:
                    success = False
                    details = f"Missing fields: {missing_fields}"
                else:
                    details = f"Total: {data['total_products_tracked']}, Explosive: {data['explosive_count']}"
            else:
                details = f"Status: {response.status_code}"
                
            self.log_test("Dashboard Stats", success, details)
            return success
        except Exception as e:
            self.log_test("Dashboard Stats", False, f"Error: {str(e)}")
            return False

    def test_get_product_detail(self, product_id):
        """Test individual product detail endpoint"""
        try:
            response = requests.get(f"{self.api_base}/products/{product_id}", timeout=10)
            success = response.status_code == 200
            
            if success:
                data = response.json()
                required_fields = ['score_breakdown', 'trend_data', 'hook_analysis', 'market_validation']
                missing_fields = [field for field in required_fields if field not in data]
                
                if missing_fields:
                    success = False
                    details = f"Missing fields: {missing_fields}"
                else:
                    details = f"Product: {data.get('name', 'N/A')}, Alpha Score: {data.get('alpha_score', 'N/A')}"
            else:
                details = f"Status: {response.status_code}"
                
            self.log_test("Product Detail", success, details)
            return success
        except Exception as e:
            self.log_test("Product Detail", False, f"Error: {str(e)}")
            return False

    def test_get_alerts(self):
        """Test alerts endpoint"""
        try:
            response = requests.get(f"{self.api_base}/alerts", timeout=10)
            success = response.status_code == 200
            
            if success:
                data = response.json()
                alert_count = len(data)
                details = f"Status: {response.status_code}, Alerts: {alert_count}"
                
                if alert_count > 0:
                    alert = data[0]
                    required_fields = ['id', 'product_id', 'alert_type', 'severity', 'message']
                    missing_fields = [field for field in required_fields if field not in alert]
                    if missing_fields:
                        details += f", Missing fields: {missing_fields}"
                        success = False
            else:
                details = f"Status: {response.status_code}"
                
            self.log_test("Get Alerts", success, details)
            return success
        except Exception as e:
            self.log_test("Get Alerts", False, f"Error: {str(e)}")
            return False

    def test_get_categories(self):
        """Test categories endpoint"""
        try:
            response = requests.get(f"{self.api_base}/categories", timeout=10)
            success = response.status_code == 200
            
            if success:
                data = response.json()
                categories = data.get('categories', [])
                details = f"Status: {response.status_code}, Categories: {len(categories)}"
            else:
                details = f"Status: {response.status_code}"
                
            self.log_test("Get Categories", success, details)
            return success
        except Exception as e:
            self.log_test("Get Categories", False, f"Error: {str(e)}")
            return False

    def test_refresh_products(self):
        """Test refresh products endpoint"""
        try:
            response = requests.post(f"{self.api_base}/products/refresh", timeout=20)
            success = response.status_code == 200
            
            if success:
                data = response.json()
                details = f"Status: {response.status_code}, Message: {data.get('message', 'N/A')}"
            else:
                details = f"Status: {response.status_code}"
                
            self.log_test("Refresh Products", success, details)
            return success
        except Exception as e:
            self.log_test("Refresh Products", False, f"Error: {str(e)}")
            return False

    def test_product_filters(self):
        """Test product filtering functionality"""
        try:
            # Test status filter
            response = requests.get(f"{self.api_base}/products?status=EXPLOSIVE", timeout=10)
            success = response.status_code == 200
            
            if success:
                data = response.json()
                # Verify all products have EXPLOSIVE status
                non_explosive = [p for p in data if p.get('status') != 'EXPLOSIVE']
                if non_explosive:
                    success = False
                    details = f"Filter failed: {len(non_explosive)} non-explosive products returned"
                else:
                    details = f"Status filter working: {len(data)} explosive products"
            else:
                details = f"Status: {response.status_code}"
                
            self.log_test("Product Status Filter", success, details)
            
            # Test score range filter with updated threshold (72+ for EXPLOSIVE)
            response = requests.get(f"{self.api_base}/products?min_score=72", timeout=10)
            success2 = response.status_code == 200
            
            if success2:
                data = response.json()
                low_score = [p for p in data if p.get('alpha_score', 0) < 72]
                if low_score:
                    success2 = False
                    details2 = f"Score filter failed: {len(low_score)} products below 72"
                else:
                    details2 = f"Score filter working: {len(data)} products >= 72"
            else:
                details2 = f"Status: {response.status_code}"
                
            self.log_test("Product Score Filter (72+ threshold)", success2, details2)
            
            return success and success2
        except Exception as e:
            self.log_test("Product Filters", False, f"Error: {str(e)}")
            return False

    def test_subscription_plans(self):
        """Test subscription plans endpoint"""
        try:
            response = requests.get(f"{self.api_base}/plans", timeout=10)
            success = response.status_code == 200
            
            if success:
                data = response.json()
                plans = data.get('plans', {})
                expected_plans = ['scout', 'hunter', 'predator']
                expected_prices = {'scout': 29.0, 'hunter': 79.0, 'predator': 199.0}
                
                missing_plans = [plan for plan in expected_plans if plan not in plans]
                if missing_plans:
                    success = False
                    details = f"Missing plans: {missing_plans}"
                else:
                    # Check prices
                    price_errors = []
                    for plan_id, expected_price in expected_prices.items():
                        actual_price = plans[plan_id].get('price')
                        if actual_price != expected_price:
                            price_errors.append(f"{plan_id}: expected ${expected_price}, got ${actual_price}")
                    
                    if price_errors:
                        success = False
                        details = f"Price errors: {price_errors}"
                    else:
                        details = f"All 3 plans found with correct prices: Scout $29, Hunter $79, Predator $199"
            else:
                details = f"Status: {response.status_code}"
                
            self.log_test("Subscription Plans", success, details)
            return success
        except Exception as e:
            self.log_test("Subscription Plans", False, f"Error: {str(e)}")
            return False

    def test_watchlist_endpoints(self):
        """Test watchlist functionality"""
        test_user_id = "test_user_123"
        success_count = 0
        total_tests = 3
        
        try:
            # Test get empty watchlist
            response = requests.get(f"{self.api_base}/watchlist/{test_user_id}", timeout=10)
            if response.status_code == 200:
                data = response.json()
                if 'watchlist' in data:
                    success_count += 1
                    self.log_test("Get Watchlist", True, f"Watchlist retrieved: {len(data['watchlist'])} items")
                else:
                    self.log_test("Get Watchlist", False, "Missing 'watchlist' field in response")
            else:
                self.log_test("Get Watchlist", False, f"Status: {response.status_code}")
            
            # Get a product ID for testing
            products_response = requests.get(f"{self.api_base}/products?limit=1", timeout=10)
            if products_response.status_code == 200:
                products = products_response.json()
                if products:
                    product_id = products[0]['id']
                    
                    # Test add to watchlist
                    response = requests.post(
                        f"{self.api_base}/watchlist/add?user_id={test_user_id}&product_id={product_id}&notes=Test note",
                        timeout=10
                    )
                    if response.status_code == 200:
                        success_count += 1
                        self.log_test("Add to Watchlist", True, f"Product {product_id} added to watchlist")
                        
                        # Test remove from watchlist
                        response = requests.delete(
                            f"{self.api_base}/watchlist/remove?user_id={test_user_id}&product_id={product_id}",
                            timeout=10
                        )
                        if response.status_code == 200:
                            success_count += 1
                            self.log_test("Remove from Watchlist", True, f"Product {product_id} removed from watchlist")
                        else:
                            self.log_test("Remove from Watchlist", False, f"Status: {response.status_code}")
                    else:
                        self.log_test("Add to Watchlist", False, f"Status: {response.status_code}")
                        self.log_test("Remove from Watchlist", False, "Skipped due to add failure")
                else:
                    self.log_test("Add to Watchlist", False, "No products available for testing")
                    self.log_test("Remove from Watchlist", False, "Skipped due to no products")
            else:
                self.log_test("Add to Watchlist", False, "Failed to get products for testing")
                self.log_test("Remove from Watchlist", False, "Skipped due to product fetch failure")
                
            return success_count == total_tests
        except Exception as e:
            self.log_test("Watchlist Endpoints", False, f"Error: {str(e)}")
            return False

    def test_checkout_create(self):
        """Test Stripe checkout creation"""
        try:
            response = requests.post(
                f"{self.api_base}/checkout/create?plan_id=scout&user_email=test@example.com",
                timeout=15
            )
            success = response.status_code == 200
            
            if success:
                data = response.json()
                required_fields = ['checkout_url', 'session_id', 'plan']
                missing_fields = [field for field in required_fields if field not in data]
                
                if missing_fields:
                    success = False
                    details = f"Missing fields: {missing_fields}"
                else:
                    details = f"Checkout session created: {data['session_id'][:20]}..."
            else:
                details = f"Status: {response.status_code}"
                if response.status_code == 500:
                    details += " (Expected if Stripe not fully configured)"
                
            self.log_test("Stripe Checkout Create", success, details)
            return success
        except Exception as e:
            self.log_test("Stripe Checkout Create", False, f"Error: {str(e)}")
            return False

    def test_cron_refresh_endpoint(self):
        """Test cron refresh data endpoint"""
        try:
            # Test without API key (should fail)
            response = requests.post(f"{self.api_base}/cron/refresh-data", timeout=20)
            if response.status_code == 401:
                self.log_test("Cron Endpoint Security", True, "Correctly rejected request without API key")
            else:
                self.log_test("Cron Endpoint Security", False, f"Expected 401, got {response.status_code}")
            
            # Test with API key
            response = requests.post(
                f"{self.api_base}/cron/refresh-data?api_key=alpha-drop-cron-2024",
                timeout=30
            )
            success = response.status_code == 200
            
            if success:
                data = response.json()
                if 'success' in data:
                    details = f"Cron refresh: {data.get('success', False)}, Products: {data.get('products_loaded', 0)}"
                else:
                    details = "Cron endpoint responded but missing success field"
            else:
                details = f"Status: {response.status_code}"
                
            self.log_test("Cron Refresh Data", success, details)
            return success
        except Exception as e:
            self.log_test("Cron Refresh Data", False, f"Error: {str(e)}")
            return False

    def test_beta_signup_endpoints(self):
        """Test beta signup functionality"""
        try:
            test_email = f"test_{datetime.now().strftime('%H%M%S')}@example.com"
            
            # Test beta signup
            response = requests.post(
                f"{self.api_base}/beta/signup?email={test_email}&name=Test User",
                timeout=10
            )
            success = response.status_code == 200
            
            if success:
                data = response.json()
                required_fields = ['message', 'status', 'position']
                missing_fields = [field for field in required_fields if field not in data]
                
                if missing_fields:
                    success = False
                    details = f"Missing fields: {missing_fields}"
                else:
                    details = f"Beta signup successful: position {data.get('position', 'N/A')}, status: {data.get('status')}"
            else:
                details = f"Status: {response.status_code}"
                
            self.log_test("Beta Signup", success, details)
            
            # Test beta stats
            response = requests.get(f"{self.api_base}/beta/stats", timeout=10)
            success2 = response.status_code == 200
            
            if success2:
                data = response.json()
                required_fields = ['total_signups', 'pending', 'invited']
                missing_fields = [field for field in required_fields if field not in data]
                
                if missing_fields:
                    success2 = False
                    details2 = f"Missing fields: {missing_fields}"
                else:
                    details2 = f"Beta stats: {data.get('total_signups', 0)} total signups, {data.get('pending', 0)} pending"
            else:
                details2 = f"Status: {response.status_code}"
                
            self.log_test("Beta Stats", success2, details2)
            
            return success and success2
        except Exception as e:
            self.log_test("Beta Signup Endpoints", False, f"Error: {str(e)}")
            return False

    def test_auth_endpoints(self):
        """Test authentication endpoints (without actual OAuth)"""
        try:
            # Test /auth/me without authentication (should fail)
            response = requests.get(f"{self.api_base}/auth/me", timeout=10)
            if response.status_code == 401:
                self.log_test("Auth Me (Unauthenticated)", True, "Correctly rejected unauthenticated request")
                auth_success = True
            else:
                self.log_test("Auth Me (Unauthenticated)", False, f"Expected 401, got {response.status_code}")
                auth_success = False
            
            # Test auth/session endpoint (without valid session_id, should fail)
            response = requests.post(f"{self.api_base}/auth/session?session_id=invalid_session", timeout=10)
            if response.status_code == 401:
                self.log_test("Auth Session (Invalid)", True, "Correctly rejected invalid session")
                session_success = True
            else:
                self.log_test("Auth Session (Invalid)", False, f"Expected 401, got {response.status_code}")
                session_success = False
            
            # Test logout endpoint
            response = requests.post(f"{self.api_base}/auth/logout", timeout=10)
            logout_success = response.status_code == 200
            
            if logout_success:
                data = response.json()
                details = f"Logout response: {data.get('message', 'N/A')}"
            else:
                details = f"Status: {response.status_code}"
                
            self.log_test("Auth Logout", logout_success, details)
            
            return auth_success and session_success and logout_success
        except Exception as e:
            self.log_test("Auth Endpoints", False, f"Error: {str(e)}")
            return False

    def test_notifications_endpoint(self):
        """Test email notifications endpoint (requires auth)"""
        try:
            # Test without authentication (should fail)
            response = requests.post(f"{self.api_base}/notifications/test", timeout=10)
            success = response.status_code == 401
            
            if success:
                details = "Correctly rejected unauthenticated notification request"
            else:
                details = f"Expected 401, got {response.status_code}"
                
            self.log_test("Notifications Test (Auth Required)", success, details)
            return success
        except Exception as e:
            self.log_test("Notifications Test", False, f"Error: {str(e)}")
            return False

    def test_alpha_score_thresholds(self):
        """Test updated Alpha Score thresholds (72+ for EXPLOSIVE)"""
        try:
            response = requests.get(f"{self.api_base}/stats", timeout=10)
            success = response.status_code == 200
            
            if success:
                stats = response.json()
                explosive_count = stats.get('explosive_count', 0)
                
                # Get explosive products to verify threshold
                response = requests.get(f"{self.api_base}/products?status=EXPLOSIVE", timeout=10)
                if response.status_code == 200:
                    explosive_products = response.json()
                    
                    # Check if any explosive products have score < 72
                    low_score_explosive = [p for p in explosive_products if p.get('alpha_score', 0) < 72]
                    
                    if low_score_explosive:
                        success = False
                        details = f"Found {len(low_score_explosive)} explosive products with score < 72"
                    else:
                        details = f"Threshold correct: {len(explosive_products)} explosive products all >= 72 score"
                        
                        # Check if we have 83+ explosive products as mentioned in requirements
                        if explosive_count >= 83:
                            details += f" ({explosive_count} total, meeting 83+ requirement)"
                        else:
                            details += f" ({explosive_count} total, below 83+ target)"
                else:
                    details = f"Stats show {explosive_count} explosive products"
            else:
                details = f"Status: {response.status_code}"
                
            self.log_test("Alpha Score Thresholds (72+ EXPLOSIVE)", success, details)
            return success
        except Exception as e:
            self.log_test("Alpha Score Thresholds", False, f"Error: {str(e)}")
            return False

    def run_all_tests(self):
        """Run all API tests"""
        print("🚀 Starting ALPHA DROP API Tests...")
        print("=" * 50)
        
        # Test basic connectivity
        if not self.test_api_root():
            print("❌ API root failed - stopping tests")
            return False
        
        # Test core endpoints
        products_success, products_data = self.test_get_products()
        self.test_dashboard_products()
        self.test_get_stats()
        self.test_get_alerts()
        self.test_get_categories()
        
        # Test product detail if we have products
        if products_success and products_data:
            product_id = products_data[0]['id']
            self.test_get_product_detail(product_id)
        
        # Test filtering
        self.test_product_filters()
        
        # Test refresh functionality
        self.test_refresh_products()
        
        # Test new features
        print("\n🆕 Testing New Features...")
        self.test_alpha_score_thresholds()
        self.test_subscription_plans()
        self.test_watchlist_endpoints()
        self.test_checkout_create()
        self.test_cron_refresh_endpoint()
        
        # Test ALPHA DROP specific features
        print("\n🔥 Testing ALPHA DROP Features...")
        self.test_beta_signup_endpoints()
        self.test_auth_endpoints()
        self.test_notifications_endpoint()
        
        # Print summary
        print("\n" + "=" * 50)
        print(f"📊 Test Summary: {self.tests_passed}/{self.tests_run} tests passed")
        
        if self.tests_passed == self.tests_run:
            print("🎉 All tests passed!")
            return True
        else:
            print(f"⚠️  {self.tests_run - self.tests_passed} tests failed")
            return False

def main():
    tester = AlphaDropAPITester()
    success = tester.run_all_tests()
    
    # Save detailed results
    with open('/app/backend_test_results.json', 'w') as f:
        json.dump({
            'summary': {
                'total_tests': tester.tests_run,
                'passed_tests': tester.tests_passed,
                'success_rate': f"{(tester.tests_passed/tester.tests_run*100):.1f}%" if tester.tests_run > 0 else "0%",
                'timestamp': datetime.now().isoformat()
            },
            'test_results': tester.test_results
        }, f, indent=2)
    
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())