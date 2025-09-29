#!/usr/bin/env python3
"""
API Test Runner with Environment Support

Author: Pedro Garcia
Runs API tests against either local or production environment
based on configuration in .env file.

Usage:
    # Test local environment (default)
    python3 test/run_api_tests.py
    
    # Test production environment
    python3 test/run_api_tests.py --production
"""

import sys
import os
import argparse
from pathlib import Path
from config import get_environment_info

def main():
    parser = argparse.ArgumentParser(description='Run API tests')
    parser.add_argument('--production', action='store_true', 
                       help='Test against production environment')
    parser.add_argument('--local', action='store_true',
                       help='Test against local environment (default)')
    
    args = parser.parse_args()
    
    # Set environment based on arguments
    if args.production:
        os.environ['API_ENVIRONMENT'] = 'production'
    else:
        os.environ['API_ENVIRONMENT'] = 'local'
    
    # Display environment info
    try:
        env_info = get_environment_info()
        print("=" * 60)
        print("API TEST RUNNER")
        print("=" * 60)
        print(f"Environment: {env_info['environment']}")
        print(f"API URL: {env_info['api_url']}")
        print(f"Production Mode: {env_info['is_production']}")
        print("=" * 60)
        
        if env_info['is_production']:
            print("\n🚀 Running PRODUCTION tests...")
            print("⚠️  Make sure your API is deployed and accessible!")
            
            # Run production-specific tests
            import test_production_deployment
            success = test_production_deployment.run_production_tests()
            
        else:
            print("\n🏠 Running LOCAL tests...")
            print("⚠️  Make sure your local server is running on port 5005!")
            
            # Run standard API tests
            import unittest
            loader = unittest.TestLoader()
            
            # Load test suites
            from test_api_endpoints import TestAPIEndpoints
            from test_specific_scenarios import TestSpecificScenarios
            
            suite = unittest.TestSuite()
            suite.addTests(loader.loadTestsFromTestCase(TestAPIEndpoints))
            suite.addTests(loader.loadTestsFromTestCase(TestSpecificScenarios))
            
            runner = unittest.TextTestRunner(verbosity=2)
            result = runner.run(suite)
            success = result.wasSuccessful()
        
        # Summary
        print("\n" + "=" * 60)
        if success:
            print("✅ ALL TESTS PASSED!")
            print("🎉 API is working correctly in", env_info['environment'], "environment")
        else:
            print("❌ SOME TESTS FAILED!")
            print("🔧 Check the output above for details")
        print("=" * 60)
        
        return 0 if success else 1
        
    except ValueError as e:
        print(f"❌ Configuration Error: {e}")
        print("\n📝 Setup Instructions:")
        print("1. Make sure .env file exists with proper configuration")
        print("2. For production testing, set PRODUCTION_API_URL in .env")
        print("3. For local testing, make sure API server is running")
        return 1
    except Exception as e:
        print(f"❌ Unexpected Error: {e}")
        return 1

if __name__ == '__main__':
    sys.exit(main())
