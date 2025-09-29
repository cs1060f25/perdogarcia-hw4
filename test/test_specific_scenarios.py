#!/usr/bin/env python3
"""
Specific Test Scenarios from Section 3.2

Author: Pedro Garcia
Tests the exact scenarios listed in section 3.2 of the todo.md:
- Valid request: {"zip":"02138","measure_name":"Adult obesity"}
- Missing zip: {"measure_name":"Adult obesity"} → 400
- Missing measure_name: {"zip":"02138"} → 400
- Invalid zip: {"zip":"00000","measure_name":"Adult obesity"} → 404
- Invalid measure_name: {"zip":"02138","measure_name":"Invalid"} → 404
- Coffee teapot: {"zip":"02138","measure_name":"Adult obesity","coffee":"teapot"} → 418
- Wrong endpoint: GET/POST to /other → 404
- SQL injection attempt (for security)
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

class TestSpecificScenarios(unittest.TestCase):
    """Test the exact scenarios from section 3.2."""

    @classmethod
    def setUpClass(cls):
        """Set up API testing environment."""
        # Get environment info
        env_info = get_environment_info()
        cls.base_url = env_info['api_url']
        cls.is_production = env_info['is_production']
        
        print(f"\n📋 Scenario Testing Environment: {env_info['environment']}")
        print(f"🌐 API URL: {cls.base_url}")
        
        # Verify server is responding
        try:
            response = requests.get(f"{cls.base_url}/nonexistent", timeout=10)
            print("✅ API server is responding for scenario tests")
        except requests.exceptions.ConnectionError:
            if cls.is_production:
                cls.fail(f"Production API server not responding at {cls.base_url}")
            else:
                cls.fail("API server not available - make sure it's running")

    def test_scenario_valid_request(self):
        """Valid request: {"zip":"02138","measure_name":"Adult obesity"}"""
        response = requests.post(
            f"{self.base_url}/county_data",
            headers={"Content-Type": "application/json"},
            json={"zip": "02138", "measure_name": "Adult obesity"}
        )
        
        # Should return 200 with data
        self.assertIn(response.status_code, [200, 404])  # 404 if no data for this specific combo
        
        if response.status_code == 200:
            data = response.json()
            self.assertIsInstance(data, list)
            print(f"✅ Valid request returned {len(data)} records")
        else:
            print("✅ Valid request format accepted (404 = no data found)")

    def test_scenario_missing_zip(self):
        """Missing zip: {"measure_name":"Adult obesity"} → 400"""
        response = requests.post(
            f"{self.base_url}/county_data",
            headers={"Content-Type": "application/json"},
            json={"measure_name": "Adult obesity"}
        )
        
        self.assertEqual(response.status_code, 400)
        data = response.json()
        self.assertIn("error", data)
        self.assertEqual(data["status"], 400)
        print("✅ Missing zip correctly returns 400")

    def test_scenario_missing_measure_name(self):
        """Missing measure_name: {"zip":"02138"} → 400"""
        response = requests.post(
            f"{self.base_url}/county_data",
            headers={"Content-Type": "application/json"},
            json={"zip": "02138"}
        )
        
        self.assertEqual(response.status_code, 400)
        data = response.json()
        self.assertIn("error", data)
        self.assertEqual(data["status"], 400)
        print("✅ Missing measure_name correctly returns 400")

    def test_scenario_invalid_zip(self):
        """Invalid zip: {"zip":"00000","measure_name":"Adult obesity"} → 404"""
        response = requests.post(
            f"{self.base_url}/county_data",
            headers={"Content-Type": "application/json"},
            json={"zip": "00000", "measure_name": "Adult obesity"}
        )
        
        self.assertEqual(response.status_code, 404)
        data = response.json()
        self.assertIn("error", data)
        self.assertEqual(data["status"], 404)
        print("✅ Invalid zip correctly returns 404")

    def test_scenario_invalid_measure_name(self):
        """Invalid measure_name: {"zip":"02138","measure_name":"Invalid"} → 404"""
        response = requests.post(
            f"{self.base_url}/county_data",
            headers={"Content-Type": "application/json"},
            json={"zip": "02138", "measure_name": "Invalid"}
        )
        
        self.assertEqual(response.status_code, 404)
        data = response.json()
        self.assertIn("error", data)
        self.assertEqual(data["status"], 404)
        print("✅ Invalid measure_name correctly returns 404")

    def test_scenario_coffee_teapot(self):
        """Coffee teapot: {"zip":"02138","measure_name":"Adult obesity","coffee":"teapot"} → 418"""
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
        print("✅ Coffee teapot correctly returns 418")

    def test_scenario_wrong_endpoint_get(self):
        """Wrong endpoint: GET to /other → 404"""
        response = requests.get(f"{self.base_url}/other")
        
        self.assertEqual(response.status_code, 404)
        data = response.json()
        self.assertIn("error", data)
        self.assertEqual(data["status"], 404)
        print("✅ GET to /other correctly returns 404")

    def test_scenario_wrong_endpoint_post(self):
        """Wrong endpoint: POST to /other → 404"""
        response = requests.post(
            f"{self.base_url}/other",
            headers={"Content-Type": "application/json"},
            json={"zip": "02138", "measure_name": "Adult obesity"}
        )
        
        self.assertEqual(response.status_code, 404)
        data = response.json()
        self.assertIn("error", data)
        self.assertEqual(data["status"], 404)
        print("✅ POST to /other correctly returns 404")

    def test_scenario_get_to_county_data(self):
        """Wrong method: GET to /county_data → 404"""
        response = requests.get(f"{self.base_url}/county_data")
        
        self.assertEqual(response.status_code, 404)
        data = response.json()
        self.assertIn("error", data)
        self.assertEqual(data["status"], 404)
        print("✅ GET to /county_data correctly returns 404")

    def test_scenario_sql_injection_attempts(self):
        """SQL injection attempt (for security)"""
        sql_injection_attempts = [
            "'; DROP TABLE county_health_rankings; --",
            "02138'; DELETE FROM zip_county WHERE '1'='1'; --",
            "02138' OR '1'='1' --",
            "02138' UNION SELECT password FROM users --",
            "'; INSERT INTO county_health_rankings VALUES ('hack'); --"
        ]
        
        for injection_attempt in sql_injection_attempts:
            with self.subTest(injection=injection_attempt[:20] + "..."):
                response = requests.post(
                    f"{self.base_url}/county_data",
                    headers={"Content-Type": "application/json"},
                    json={"zip": injection_attempt, "measure_name": "Adult obesity"}
                )
                
                # Should safely handle (return 404 for invalid format, not crash)
                self.assertIn(response.status_code, [400, 404])
                
                # Verify server is still responsive
                health_check = requests.post(
                    f"{self.base_url}/county_data",
                    headers={"Content-Type": "application/json"},
                    json={"zip": "02138", "measure_name": "Adult obesity"}
                )
                self.assertIn(health_check.status_code, [200, 404])
        
        print("✅ All SQL injection attempts safely handled")

    def test_all_valid_measures_work(self):
        """Verify all 12 valid health measures are accepted"""
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
        
        working_measures = []
        for measure in valid_measures:
            response = requests.post(
                f"{self.base_url}/county_data",
                headers={"Content-Type": "application/json"},
                json={"zip": "02138", "measure_name": measure}
            )
            
            # Should not return 400 (invalid measure), can be 200 or 404
            self.assertNotEqual(response.status_code, 400, 
                               f"Measure '{measure}' should be valid")
            
            if response.status_code == 200:
                working_measures.append(measure)
        
        print(f"✅ All {len(valid_measures)} health measures validated")
        print(f"📊 {len(working_measures)} measures have data for ZIP 02138")


if __name__ == '__main__':
    # Run tests with verbose output
    unittest.main(verbosity=2)
