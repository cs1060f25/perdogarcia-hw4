#!/usr/bin/env python3
"""
API Endpoint Test Suite for County Health Data API

Author: Pedro Garcia
Tests the REST API endpoints including:
- POST /county_data with valid requests
- Error handling (400, 404, 418)
- Valid health measures validation
- Output format verification
- SQL injection protection
"""

import unittest
import requests
import json
import time
import subprocess
import sys
import os
from pathlib import Path
from config import get_api_base_url, is_production_environment, get_environment_info

class TestAPIEndpoints(unittest.TestCase):
    """Test suite for API endpoints."""

    @classmethod
    def setUpClass(cls):
        """Set up API testing environment."""
        # Get environment info
        env_info = get_environment_info()
        cls.base_url = env_info['api_url']
        cls.is_production = env_info['is_production']
        cls.api_process = None
        
        print(f"\n🔧 Testing Environment: {env_info['environment']}")
        print(f"🌐 API URL: {cls.base_url}")
        
        if not cls.is_production:
            # Start local API server for development testing
            project_root = Path(__file__).parent.parent
            api_script = project_root / 'api' / 'index.py'
            
            cls.api_process = subprocess.Popen([
                sys.executable, str(api_script)
            ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            
            # Wait for server to start
            time.sleep(3)
            print("🚀 Local server started")
        
        # Verify server is responding
        try:
            response = requests.get(f"{cls.base_url}/nonexistent", timeout=10)
            # Should get 404, but server is responding
            print("✅ API server is responding")
        except requests.exceptions.ConnectionError:
            if cls.is_production:
                cls.fail(f"Production API server not responding at {cls.base_url}")
            else:
                cls.fail("Local API server failed to start")

    @classmethod
    def tearDownClass(cls):
        """Stop the API server after tests."""
        if cls.api_process:
            cls.api_process.terminate()
            cls.api_process.wait()

    def test_valid_health_measures(self):
        """Test all valid health measures from section 2.4."""
        valid_measures = [
            "Violent crime rate",
            "Unemployment", 
            "Children in poverty",
            "Diabetic screening",
            "Mammography screening",
            "Preventable hospital stays",
            "Uninsured",
            "Sexually transmitted infections",
            "Physical inactivity",
            "Adult obesity",
            "Premature Death",
            "Daily fine particulate matter"
        ]
        
        for measure in valid_measures:
            with self.subTest(measure=measure):
                response = requests.post(
                    f"{self.base_url}/county_data",
                    headers={"Content-Type": "application/json"},
                    json={"zip": "02138", "measure_name": measure}
                )
                
                # Should return 200 (success) or 404 (no data), but not 400 (invalid measure)
                self.assertIn(response.status_code, [200, 404], 
                             f"Measure '{measure}' should be valid but got {response.status_code}")
                
                if response.status_code != 400:
                    # If not a validation error, it means the measure is recognized as valid
                    data = response.json()
                    if response.status_code == 200:
                        self.assertIsInstance(data, list)
                        if len(data) > 0:
                            self.assertEqual(data[0]["measure_name"], measure)

    def test_output_format_schema(self):
        """Test that output format matches county_health_rankings schema (section 2.5)."""
        expected_fields = [
            "confidence_interval_lower_bound",
            "confidence_interval_upper_bound", 
            "county",
            "county_code",
            "data_release_year",
            "denominator",
            "fipscode",
            "measure_id",
            "measure_name",
            "numerator",
            "raw_value",
            "state",
            "state_code",
            "year_span"
        ]
        
        response = requests.post(
            f"{self.base_url}/county_data",
            headers={"Content-Type": "application/json"},
            json={"zip": "02138", "measure_name": "Adult obesity"}
        )
        
        if response.status_code == 200:
            data = response.json()
            self.assertIsInstance(data, list)
            if len(data) > 0:
                record = data[0]
                
                # Verify all expected fields are present
                for field in expected_fields:
                    self.assertIn(field, record, f"Missing field: {field}")
                
                # Verify no unexpected fields
                for field in record.keys():
                    self.assertIn(field, expected_fields, f"Unexpected field: {field}")

    def test_post_request_acceptance(self):
        """Test that /county_data endpoint accepts POST requests (section 2.2)."""
        response = requests.post(
            f"{self.base_url}/county_data",
            headers={"Content-Type": "application/json"},
            json={"zip": "02138", "measure_name": "Adult obesity"}
        )
        
        # Should not return 405 (Method Not Allowed)
        self.assertNotEqual(response.status_code, 405)
        self.assertIn(response.status_code, [200, 400, 404, 418])

    def test_json_input_output_handling(self):
        """Test JSON input/output handling with content-type application/json (section 2.2)."""
        # Test with proper JSON
        response = requests.post(
            f"{self.base_url}/county_data",
            headers={"Content-Type": "application/json"},
            json={"zip": "02138", "measure_name": "Adult obesity"}
        )
        
        # Should handle JSON properly
        self.assertIn(response.status_code, [200, 404])
        
        # Response should be JSON
        self.assertEqual(response.headers.get("content-type"), "application/json")
        
        # Should be able to parse response as JSON
        data = response.json()
        self.assertIsInstance(data, (list, dict))

    def test_zip_validation(self):
        """Test ZIP code validation - must be 5 digits (section 2.2)."""
        test_cases = [
            ("12345", [200, 404]),  # Valid format
            ("02138", [200, 404]),  # Valid with leading zero
            ("1234", [404]),        # Too short
            ("123456", [404]),      # Too long  
            ("abcde", [404]),       # Non-numeric
            ("", [400]),            # Empty
        ]
        
        for zip_code, expected_codes in test_cases:
            with self.subTest(zip_code=zip_code):
                response = requests.post(
                    f"{self.base_url}/county_data",
                    headers={"Content-Type": "application/json"},
                    json={"zip": zip_code, "measure_name": "Adult obesity"}
                )
                
                self.assertIn(response.status_code, expected_codes,
                             f"ZIP '{zip_code}' got {response.status_code}, expected one of {expected_codes}")

    def test_error_handling_400_missing_parameters(self):
        """Test 400 Bad Request for missing parameters (section 2.2)."""
        # Missing zip
        response = requests.post(
            f"{self.base_url}/county_data",
            headers={"Content-Type": "application/json"},
            json={"measure_name": "Adult obesity"}
        )
        self.assertEqual(response.status_code, 400)
        data = response.json()
        self.assertIn("error", data)
        self.assertEqual(data["status"], 400)
        
        # Missing measure_name
        response = requests.post(
            f"{self.base_url}/county_data",
            headers={"Content-Type": "application/json"},
            json={"zip": "02138"}
        )
        self.assertEqual(response.status_code, 400)
        data = response.json()
        self.assertIn("error", data)
        self.assertEqual(data["status"], 400)

    def test_error_handling_404_invalid_data(self):
        """Test 404 Not Found for invalid zip/measure pairs (section 2.2)."""
        # Invalid ZIP code
        response = requests.post(
            f"{self.base_url}/county_data",
            headers={"Content-Type": "application/json"},
            json={"zip": "00000", "measure_name": "Adult obesity"}
        )
        self.assertEqual(response.status_code, 404)
        data = response.json()
        self.assertIn("error", data)
        self.assertEqual(data["status"], 404)
        
        # Invalid measure name
        response = requests.post(
            f"{self.base_url}/county_data",
            headers={"Content-Type": "application/json"},
            json={"zip": "02138", "measure_name": "Invalid Measure"}
        )
        self.assertEqual(response.status_code, 404)
        data = response.json()
        self.assertIn("error", data)
        self.assertEqual(data["status"], 404)

    def test_error_handling_404_wrong_endpoints(self):
        """Test 404 Not Found for wrong endpoints (section 2.2)."""
        # Wrong endpoint
        response = requests.post(
            f"{self.base_url}/wrong_endpoint",
            headers={"Content-Type": "application/json"},
            json={"zip": "02138", "measure_name": "Adult obesity"}
        )
        self.assertEqual(response.status_code, 404)
        
        # GET request to county_data (should be POST only)
        response = requests.get(f"{self.base_url}/county_data")
        self.assertEqual(response.status_code, 404)

    def test_coffee_teapot_418(self):
        """Test HTTP 418 for coffee=teapot parameter (section 2.2)."""
        response = requests.post(
            f"{self.base_url}/county_data",
            headers={"Content-Type": "application/json"},
            json={
                "zip": "02138", 
                "measure_name": "Adult obesity",
                "coffee": "teapot"
            }
        )
        
        self.assertEqual(response.status_code, 418)
        data = response.json()
        self.assertIn("error", data)
        self.assertEqual(data["status"], 418)

    def test_sql_injection_protection(self):
        """Test SQL injection protection with parameterized queries (section 2.3)."""
        malicious_inputs = [
            "'; DROP TABLE county_health_rankings; --",
            "02138'; DELETE FROM zip_county; --",
            "02138' OR '1'='1",
            "02138' UNION SELECT * FROM sqlite_master --"
        ]
        
        for malicious_zip in malicious_inputs:
            with self.subTest(malicious_input=malicious_zip):
                response = requests.post(
                    f"{self.base_url}/county_data",
                    headers={"Content-Type": "application/json"},
                    json={"zip": malicious_zip, "measure_name": "Adult obesity"}
                )
                
                # Should handle safely (404 for invalid format, not crash)
                self.assertIn(response.status_code, [400, 404])
                
                # Server should still be responding (not crashed)
                health_check = requests.post(
                    f"{self.base_url}/county_data",
                    headers={"Content-Type": "application/json"},
                    json={"zip": "02138", "measure_name": "Adult obesity"}
                )
                self.assertIn(health_check.status_code, [200, 404])

    def test_database_join_logic(self):
        """Test that database join logic works: zip → county → health data (section 2.3)."""
        response = requests.post(
            f"{self.base_url}/county_data",
            headers={"Content-Type": "application/json"},
            json={"zip": "02138", "measure_name": "Adult obesity"}
        )
        
        if response.status_code == 200:
            data = response.json()
            self.assertIsInstance(data, list)
            if len(data) > 0:
                record = data[0]
                
                # Should have county information (from join)
                self.assertIn("county", record)
                self.assertIn("state", record)
                self.assertIn("fipscode", record)
                
                # Should have health measure data
                self.assertEqual(record["measure_name"], "Adult obesity")
                self.assertIn("raw_value", record)

    def test_successful_request_format(self):
        """Test successful request returns proper format (section 3.2)."""
        response = requests.post(
            f"{self.base_url}/county_data",
            headers={"Content-Type": "application/json"},
            json={"zip": "02138", "measure_name": "Adult obesity"}
        )
        
        if response.status_code == 200:
            data = response.json()
            
            # Should return array of records
            self.assertIsInstance(data, list)
            
            # Each record should match county_health_rankings schema
            for record in data:
                self.assertIsInstance(record, dict)
                self.assertIn("measure_name", record)
                self.assertEqual(record["measure_name"], "Adult obesity")


if __name__ == '__main__':
    # Run tests with verbose output
    unittest.main(verbosity=2)
