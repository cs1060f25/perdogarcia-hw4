#!/usr/bin/env python3
"""
Test runner for csv_to_sqlite.py

This script runs all tests and provides a summary of results.
Use this to verify that csv_to_sqlite.py works correctly.

Usage:
    python3 test/run_tests.py
"""

import sys
import os
import subprocess
import sqlite3
from pathlib import Path

def run_basic_functionality_test():
    """Test basic CSV to SQLite conversion with the actual project files."""
    print("=" * 60)
    print("BASIC FUNCTIONALITY TEST")
    print("=" * 60)
    
    project_root = Path(__file__).parent.parent
    script_path = project_root / 'csv_to_sqlite.py'
    test_db = project_root / 'test_data.db'
    zip_csv = project_root / 'zip_county.csv'
    health_csv = project_root / 'county_health_rankings.csv'
    
    # Clean up any existing test database
    if test_db.exists():
        test_db.unlink()
    
    success = True
    
    # Test 1: Convert zip_county.csv
    print(f"1. Converting {zip_csv.name}...")
    result = subprocess.run([
        sys.executable, str(script_path), str(test_db), str(zip_csv)
    ], capture_output=True, text=True)
    
    if result.returncode != 0:
        print(f"   ❌ FAILED: {result.stderr}")
        success = False
    else:
        print(f"   ✅ SUCCESS")
    
    # Test 2: Convert county_health_rankings.csv
    print(f"2. Converting {health_csv.name}...")
    result = subprocess.run([
        sys.executable, str(script_path), str(test_db), str(health_csv)
    ], capture_output=True, text=True)
    
    if result.returncode != 0:
        print(f"   ❌ FAILED: {result.stderr}")
        success = False
    else:
        print(f"   ✅ SUCCESS")
    
    # Test 3: Verify database structure
    if test_db.exists():
        print("3. Verifying database structure...")
        try:
            conn = sqlite3.connect(str(test_db))
            cursor = conn.cursor()
            
            # Check tables exist
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = [row[0] for row in cursor.fetchall()]
            
            expected_tables = ['zip_county', 'county_health_rankings']
            missing_tables = [t for t in expected_tables if t not in tables]
            
            if missing_tables:
                print(f"   ❌ MISSING TABLES: {missing_tables}")
                success = False
            else:
                print(f"   ✅ All tables created: {tables}")
            
            # Check column names (this will reveal BOM issues)
            for table in tables:
                cursor.execute(f"PRAGMA table_info({table})")
                columns = [col[1] for col in cursor.fetchall()]
                print(f"   📋 {table} columns: {columns[:3]}...")  # Show first 3 columns
                
                # Check for BOM in first column
                if columns and columns[0].startswith('\ufeff'):
                    print(f"   ⚠️  WARNING: BOM detected in {table} first column: '{columns[0]}'")
                    success = False
            
            # Test a simple query
            print("4. Testing queries...")
            try:
                # Try to query zip_county
                cursor.execute("SELECT COUNT(*) FROM zip_county")
                zip_count = cursor.fetchone()[0]
                print(f"   📊 zip_county rows: {zip_count}")
                
                cursor.execute("SELECT COUNT(*) FROM county_health_rankings") 
                health_count = cursor.fetchone()[0]
                print(f"   📊 county_health_rankings rows: {health_count}")
                
                # Try a specific lookup (this will fail if BOM issue exists)
                cursor.execute("SELECT COUNT(*) FROM zip_county WHERE zip = '02138'")
                cambridge_count = cursor.fetchone()[0]
                print(f"   🔍 Cambridge (02138) records: {cambridge_count}")
                
                if cambridge_count == 0:
                    print("   ⚠️  WARNING: Could not find Cambridge records - possible column name issue")
                    success = False
                
            except sqlite3.OperationalError as e:
                print(f"   ❌ QUERY FAILED: {e}")
                success = False
            
            conn.close()
            
        except Exception as e:
            print(f"   ❌ DATABASE ERROR: {e}")
            success = False
    
    # Clean up
    if test_db.exists():
        test_db.unlink()
    
    return success

def run_comprehensive_tests():
    """Run the full test suite."""
    print("\n" + "=" * 60)
    print("COMPREHENSIVE TEST SUITE")
    print("=" * 60)
    
    test_script = Path(__file__).parent / 'test_csv_to_sqlite.py'
    
    result = subprocess.run([
        sys.executable, str(test_script)
    ], capture_output=True, text=True)
    
    print(result.stdout)
    if result.stderr:
        print("STDERR:")
        print(result.stderr)
    
    return result.returncode == 0

def main():
    """Run all tests and provide summary."""
    print("CSV to SQLite Test Runner")
    print("Testing csv_to_sqlite.py functionality...")
    
    # Run basic functionality test
    basic_success = run_basic_functionality_test()
    
    # Run comprehensive test suite
    comprehensive_success = run_comprehensive_tests()
    
    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    
    if basic_success:
        print("✅ Basic functionality: PASSED")
    else:
        print("❌ Basic functionality: FAILED")
    
    if comprehensive_success:
        print("✅ Comprehensive tests: PASSED")
    else:
        print("❌ Comprehensive tests: FAILED")
    
    if basic_success and comprehensive_success:
        print("\n🎉 ALL TESTS PASSED! csv_to_sqlite.py is working correctly.")
        return 0
    else:
        print("\n⚠️  SOME TESTS FAILED. Please check the bug report and fix the issues.")
        print("📋 See test/bug_report.md for detailed information about the bugs.")
        return 1

if __name__ == '__main__':
    sys.exit(main())
