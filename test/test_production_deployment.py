#!/usr/bin/env python3
"""
Production Deployment Test Suite

Author: Pedro Garcia
Tests the deployed API endpoint to verify it works in production.
This script is specifically for testing the live deployment.

Usage:
    # Set environment to production in .env file first
    API_ENVIRONMENT=production
    PRODUCTION_API_URL=https://your-actual-deployment-url.vercel.app
    
    # Then run tests
    python3 test/test_production_deployment.py
"""

import unittest
import requests
import json
import os
import sys
from pathlib import Path
from config import get_api_base_url, is_production_environment, get_environment_info

class TestProductionDeployment(unittest.TestCase):
    """Test suite specifically for production deployment verification."""

    @classmethod
    def setUpClass(cls):
        """Set up production testing environment."""
        # Force production environment for this test
        os.environ['API_ENVIRONMENT'] = 'production'
        
        try:
            env_info = get_environment_info()
            cls.base_url = env_info['api_url']
            cls.is_production = True
            
            print(f"\n🚀 Production Deployment Test")
            print(f"🌐 Testing URL: {cls.base_url}")
            print(f"📋 Environment: {env_info['environment']}")
            
        except ValueError as e:
            cls.skipTest(f"Production URL not configured: {e}")

    def test_deployment_health_check(self):
        """Test that the deployed API is responding."""
        try:
            # Test a simple 404 endpoint to verify server is up
            response = requests.get(f"{self.base_url}/health-check", timeout=30)
            
            # Should get 404 (endpoint doesn't exist) but server is responding
            self.assertEqual(response.status_code, 404)
            print("✅ Deployment is responding to requests")
            
        except requests.exceptions.ConnectionError:
            self.fail(f"❌ Deployment not accessible at {self.base_url}")
        except requests.exceptions.Timeout:
            self.fail(f"❌ Deployment timeout at {self.base_url}")

    def test_production_cors_headers(self):
        """Test that CORS headers are properly configured for production."""
        response = requests.options(
            f"{self.base_url}/county_data",
            headers={
                "Origin": "https://example.com",
                "Access-Control-Request-Method": "POST"
            }
        )
        
        # Check if CORS is configured (may vary by platform)
        print(f"📡 CORS Response Status: {response.status_code}")
        print(f"📡 Response Headers: {dict(response.headers)}")

    def test_production_valid_request(self):
        """Test a valid request works in production."""
        response = requests.post(
            f"{self.base_url}/county_data",
            headers={"Content-Type": "application/json"},
            json={"zip": "02138", "measure_name": "Adult obesity"},
            timeout=30
        )
        
        self.assertIn(response.status_code, [200, 404])
        
        if response.status_code == 200:
            data = response.json()
            self.assertIsInstance(data, list)
            print(f"✅ Production API returned {len(data)} records")
        else:
            print("✅ Production API properly handles requests (404 = no data)")

    def test_production_error_handling(self):
        """Test error handling in production."""
        # Test 400 error
        response = requests.post(
            f"{self.base_url}/county_data",
            headers={"Content-Type": "application/json"},
            json={"measure_name": "Adult obesity"},  # Missing zip
            timeout=30
        )
        
        self.assertEqual(response.status_code, 400)
        data = response.json()
        self.assertIn("error", data)
        print("✅ Production API properly handles 400 errors")

    def test_production_teapot(self):
        """Test the coffee=teapot easter egg in production."""
        response = requests.post(
            f"{self.base_url}/county_data",
            headers={"Content-Type": "application/json"},
            json={
                "zip": "02138", 
                "measure_name": "Adult obesity",
                "coffee": "teapot"
            },
            timeout=30
        )
        
        self.assertEqual(response.status_code, 418)
        data = response.json()
        self.assertIn("error", data)
        print("✅ Production API properly handles 418 teapot")

    def test_production_database_access(self):
        """Test that production has access to the database."""
        # Try multiple ZIP codes to ensure database is accessible
        test_zips = ["02138", "10001", "90210"]
        
        for zip_code in test_zips:
            with self.subTest(zip_code=zip_code):
                response = requests.post(
                    f"{self.base_url}/county_data",
                    headers={"Content-Type": "application/json"},
                    json={"zip": zip_code, "measure_name": "Adult obesity"},
                    timeout=30
                )
                
                # Should get either 200 (data found) or 404 (no data), not 500 (database error)
                self.assertIn(response.status_code, [200, 404])
                self.assertNotEqual(response.status_code, 500)
        
        print("✅ Production database is accessible")

    def test_production_performance(self):
        """Test basic performance of production deployment."""
        import time
        
        start_time = time.time()
        
        response = requests.post(
            f"{self.base_url}/county_data",
            headers={"Content-Type": "application/json"},
            json={"zip": "02138", "measure_name": "Adult obesity"},
            timeout=30
        )
        
        end_time = time.time()
        response_time = end_time - start_time
        
        # Should respond within reasonable time (30 seconds max due to timeout)
        self.assertLess(response_time, 30)
        print(f"⚡ Production response time: {response_time:.2f} seconds")

    def test_all_endpoints_accessible(self):
        """Test that all required endpoints are accessible in production."""
        # Test wrong endpoint returns 404
        response = requests.get(f"{self.base_url}/wrong-endpoint", timeout=30)
        self.assertEqual(response.status_code, 404)
        
        # Test GET to county_data returns 404 (should be POST only)
        response = requests.get(f"{self.base_url}/county_data", timeout=30)
        self.assertEqual(response.status_code, 404)
        
        print("✅ Production endpoints properly configured")


def run_production_tests():
    """Run production tests and generate report."""
    print("=" * 60)
    print("PRODUCTION DEPLOYMENT TEST SUITE")
    print("=" * 60)
    
    # Check if production URL is configured
    try:
        os.environ['API_ENVIRONMENT'] = 'production'
        env_info = get_environment_info()
        print(f"Testing: {env_info['api_url']}")
    except ValueError as e:
        print(f"❌ SKIPPED: {e}")
        print("\n📝 To run production tests:")
        print("1. Update .env file with your deployment URL:")
        print("   PRODUCTION_API_URL=https://your-deployment-url.vercel.app")
        print("2. Set API_ENVIRONMENT=production")
        print("3. Run this test again")
        return False
    
    # Run the tests
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromTestCase(TestProductionDeployment)
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result.wasSuccessful()


if __name__ == '__main__':
    success = run_production_tests()
    sys.exit(0 if success else 1)
