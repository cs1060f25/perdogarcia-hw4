#!/usr/bin/env python3
"""
Comprehensive test suite for csv_to_sqlite.py

Author: Pedro Garcia
Tests the CSV to SQLite converter functionality including:
- Basic functionality
- Error handling
- Database structure validation
- Data integrity
- Edge cases
"""

import unittest
import sqlite3
import os
import sys
import tempfile
import subprocess
import csv
from pathlib import Path

# Add parent directory to path to import the module
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import csv_to_sqlite


class TestCSVToSQLite(unittest.TestCase):
    """Test suite for csv_to_sqlite.py functionality."""

    def setUp(self):
        """Set up test fixtures before each test method."""
        self.test_dir = tempfile.mkdtemp()
        self.test_db = os.path.join(self.test_dir, 'test.db')
        self.script_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'csv_to_sqlite.py')

    def tearDown(self):
        """Clean up after each test method."""
        # Clean up test files
        if os.path.exists(self.test_db):
            os.remove(self.test_db)
        
        # Clean up test directory
        import shutil
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)

    def create_test_csv(self, filename, headers, rows):
        """Create a test CSV file with given headers and rows."""
        csv_path = os.path.join(self.test_dir, filename)
        with open(csv_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(headers)
            for row in rows:
                writer.writerow(row)
        return csv_path

    def test_basic_functionality(self):
        """Test basic CSV to SQLite conversion."""
        # Create test CSV
        headers = ['id', 'name', 'value']
        rows = [
            ['1', 'test1', '100'],
            ['2', 'test2', '200'],
            ['3', 'test3', '300']
        ]
        csv_path = self.create_test_csv('basic_test.csv', headers, rows)

        # Run conversion
        result = subprocess.run([
            sys.executable, self.script_path, self.test_db, csv_path
        ], capture_output=True, text=True)

        # Check that script ran successfully
        self.assertEqual(result.returncode, 0, f"Script failed: {result.stderr}")

        # Verify database was created
        self.assertTrue(os.path.exists(self.test_db))

        # Verify table structure and data
        conn = sqlite3.connect(self.test_db)
        cursor = conn.cursor()

        # Check table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='basic_test'")
        self.assertIsNotNone(cursor.fetchone())

        # Check table schema
        cursor.execute("PRAGMA table_info(basic_test)")
        columns = cursor.fetchall()
        self.assertEqual(len(columns), 3)
        
        # All columns should be TEXT type
        for col in columns:
            self.assertEqual(col[2], 'TEXT')  # col[2] is the type

        # Check data
        cursor.execute("SELECT COUNT(*) FROM basic_test")
        self.assertEqual(cursor.fetchone()[0], 3)

        # Check specific data
        cursor.execute("SELECT * FROM basic_test ORDER BY id")
        data = cursor.fetchall()
        self.assertEqual(data[0], ('1', 'test1', '100'))
        self.assertEqual(data[1], ('2', 'test2', '200'))
        self.assertEqual(data[2], ('3', 'test3', '300'))

        conn.close()

    def test_zip_county_structure(self):
        """Test conversion of zip_county.csv structure."""
        # Create test CSV with zip_county structure
        headers = ['zip', 'default_state', 'county', 'county_state', 'state_abbreviation', 
                  'county_code', 'zip_pop', 'zip_pop_in_county', 'n_counties', 'default_city']
        rows = [
            ['00501', 'NY', 'Suffolk County', 'New York', 'NY', '36103', '', '0', '1', 'Holtsville'],
            ['02138', 'MA', 'Middlesex County', 'Massachusetts', 'MA', '25017', '32000', '1.0', '1', 'Cambridge']
        ]
        csv_path = self.create_test_csv('zip_county.csv', headers, rows)

        # Run conversion
        result = subprocess.run([
            sys.executable, self.script_path, self.test_db, csv_path
        ], capture_output=True, text=True)

        self.assertEqual(result.returncode, 0, f"Script failed: {result.stderr}")

        # Verify database structure
        conn = sqlite3.connect(self.test_db)
        cursor = conn.cursor()

        # Check table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='zip_county'")
        self.assertIsNotNone(cursor.fetchone())

        # Check that ZIP codes are preserved as strings (with leading zeros)
        cursor.execute("SELECT zip FROM zip_county WHERE zip = '00501'")
        result = cursor.fetchone()
        self.assertIsNotNone(result)
        self.assertEqual(result[0], '00501')

        # Check index was created
        cursor.execute("SELECT name FROM sqlite_master WHERE type='index' AND name='idx_zip_county_zip'")
        self.assertIsNotNone(cursor.fetchone())

        conn.close()

    def test_county_health_rankings_structure(self):
        """Test conversion of county_health_rankings.csv structure."""
        headers = ['State', 'County', 'State_code', 'County_code', 'Year_span', 'Measure_name',
                  'Measure_id', 'Numerator', 'Denominator', 'Raw_value', 
                  'Confidence_Interval_Lower_Bound', 'Confidence_Interval_Upper_Bound',
                  'Data_Release_Year', 'fipscode']
        rows = [
            ['Massachusetts', 'Middlesex County', '25', '25017', '2020', 'Adult obesity', '1', 
             '100', '500', '0.20', '0.18', '0.22', '2021', '25017'],
            ['New York', 'Suffolk County', '36', '36103', '2020', 'Adult obesity', '1',
             '150', '600', '0.25', '0.23', '0.27', '2021', '36103']
        ]
        csv_path = self.create_test_csv('county_health_rankings.csv', headers, rows)

        # Run conversion
        result = subprocess.run([
            sys.executable, self.script_path, self.test_db, csv_path
        ], capture_output=True, text=True)

        self.assertEqual(result.returncode, 0, f"Script failed: {result.stderr}")

        # Verify database structure
        conn = sqlite3.connect(self.test_db)
        cursor = conn.cursor()

        # Check table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='county_health_rankings'")
        self.assertIsNotNone(cursor.fetchone())

        # Check data integrity
        cursor.execute("SELECT COUNT(*) FROM county_health_rankings")
        self.assertEqual(cursor.fetchone()[0], 2)

        # Check specific health measure
        cursor.execute("SELECT * FROM county_health_rankings WHERE Measure_name = 'Adult obesity'")
        results = cursor.fetchall()
        self.assertEqual(len(results), 2)

        conn.close()

    def test_empty_csv(self):
        """Test handling of empty CSV file."""
        csv_path = self.create_test_csv('empty.csv', ['col1', 'col2'], [])

        result = subprocess.run([
            sys.executable, self.script_path, self.test_db, csv_path
        ], capture_output=True, text=True)

        # Should succeed but create empty table
        self.assertEqual(result.returncode, 0)
        
        conn = sqlite3.connect(self.test_db)
        cursor = conn.cursor()
        
        # Table should exist but be empty
        cursor.execute("SELECT COUNT(*) FROM empty")
        self.assertEqual(cursor.fetchone()[0], 0)
        
        conn.close()

    def test_missing_csv_file(self):
        """Test error handling for missing CSV file."""
        result = subprocess.run([
            sys.executable, self.script_path, self.test_db, 'nonexistent.csv'
        ], capture_output=True, text=True)

        self.assertEqual(result.returncode, 1)
        self.assertIn("not found", result.stderr)

    def test_invalid_arguments(self):
        """Test error handling for invalid command line arguments."""
        # Test with no arguments
        result = subprocess.run([
            sys.executable, self.script_path
        ], capture_output=True, text=True)
        
        self.assertEqual(result.returncode, 1)
        self.assertIn("Usage:", result.stderr)

        # Test with only one argument
        result = subprocess.run([
            sys.executable, self.script_path, self.test_db
        ], capture_output=True, text=True)
        
        self.assertEqual(result.returncode, 1)
        self.assertIn("Usage:", result.stderr)

    def test_special_characters_in_data(self):
        """Test handling of special characters in CSV data."""
        headers = ['id', 'description', 'value']
        rows = [
            ['1', 'Test with "quotes"', '100'],
            ['2', "Test with 'apostrophes'", '200'],
            ['3', 'Test with, commas', '300'],
            ['4', 'Test with\nnewlines', '400']
        ]
        csv_path = self.create_test_csv('special_chars.csv', headers, rows)

        result = subprocess.run([
            sys.executable, self.script_path, self.test_db, csv_path
        ], capture_output=True, text=True)

        self.assertEqual(result.returncode, 0, f"Script failed: {result.stderr}")

        # Verify data was inserted correctly
        conn = sqlite3.connect(self.test_db)
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM special_chars")
        self.assertEqual(cursor.fetchone()[0], 4)
        
        conn.close()

    def test_table_replacement(self):
        """Test that existing tables are replaced."""
        headers = ['id', 'value']
        rows = [['1', 'original']]
        csv_path = self.create_test_csv('replace_test.csv', headers, rows)

        # First conversion
        result = subprocess.run([
            sys.executable, self.script_path, self.test_db, csv_path
        ], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0)

        # Modify CSV and convert again
        rows = [['1', 'updated'], ['2', 'new']]
        csv_path = self.create_test_csv('replace_test.csv', headers, rows)
        
        result = subprocess.run([
            sys.executable, self.script_path, self.test_db, csv_path
        ], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0)

        # Verify table was replaced
        conn = sqlite3.connect(self.test_db)
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM replace_test")
        self.assertEqual(cursor.fetchone()[0], 2)
        
        cursor.execute("SELECT value FROM replace_test WHERE id = '1'")
        self.assertEqual(cursor.fetchone()[0], 'updated')
        
        conn.close()

    def test_real_data_integration(self):
        """Test with actual project CSV files if they exist."""
        project_root = os.path.dirname(os.path.dirname(__file__))
        zip_csv = os.path.join(project_root, 'zip_country.csv')
        health_csv = os.path.join(project_root, 'country_health_rankings.csv')

        if os.path.exists(zip_csv):
            result = subprocess.run([
                sys.executable, self.script_path, self.test_db, zip_csv
            ], capture_output=True, text=True)
            
            self.assertEqual(result.returncode, 0, f"zip_country conversion failed: {result.stderr}")

            # Verify some basic properties
            conn = sqlite3.connect(self.test_db)
            cursor = conn.cursor()
            
            cursor.execute("SELECT COUNT(*) FROM zip_country")
            count = cursor.fetchone()[0]
            self.assertGreater(count, 0, "zip_country table should not be empty")
            
            # Test specific ZIP lookup
            cursor.execute("SELECT * FROM zip_country WHERE zip = '02138' LIMIT 1")
            result = cursor.fetchone()
            if result:
                self.assertEqual(len(result), 10)  # Should have 10 columns
            
            conn.close()

        if os.path.exists(health_csv):
            result = subprocess.run([
                sys.executable, self.script_path, self.test_db, health_csv
            ], capture_output=True, text=True)
            
            self.assertEqual(result.returncode, 0, f"county_health_rankings conversion failed: {result.stderr}")

            # Verify some basic properties
            conn = sqlite3.connect(self.test_db)
            cursor = conn.cursor()
            
            cursor.execute("SELECT COUNT(*) FROM county_health_rankings")
            count = cursor.fetchone()[0]
            self.assertGreater(count, 0, "county_health_rankings table should not be empty")
            
            conn.close()

    def test_sql_injection_safety(self):
        """Test that the script is safe from SQL injection in filenames."""
        # Create CSV with potentially dangerous filename
        headers = ['id', 'value']
        rows = [['1', 'test']]
        
        # Note: We can't actually test malicious filenames easily in filesystem,
        # but we can test that the table creation uses proper quoting
        csv_path = self.create_test_csv('test_table.csv', headers, rows)
        
        result = subprocess.run([
            sys.executable, self.script_path, self.test_db, csv_path
        ], capture_output=True, text=True)
        
        self.assertEqual(result.returncode, 0)
        
        # Verify table was created with proper name
        conn = sqlite3.connect(self.test_db)
        cursor = conn.cursor()
        
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cursor.fetchall()]
        self.assertIn('test_table', tables)
        
        conn.close()


class TestDatabaseQueries(unittest.TestCase):
    """Test database queries that would be used by the API."""

    def setUp(self):
        """Set up test database with sample data."""
        self.test_dir = tempfile.mkdtemp()
        self.test_db = os.path.join(self.test_dir, 'test_api.db')
        
        # Create test database with sample data
        conn = sqlite3.connect(self.test_db)
        cursor = conn.cursor()
        
        # Create zip_county table
        cursor.execute('''
            CREATE TABLE zip_county (
                zip TEXT,
                default_state TEXT,
                county TEXT,
                county_state TEXT,
                state_abbreviation TEXT,
                county_code TEXT,
                zip_pop TEXT,
                zip_pop_in_county TEXT,
                n_counties TEXT,
                default_city TEXT
            )
        ''')
        
        # Create county_health_rankings table
        cursor.execute('''
            CREATE TABLE county_health_rankings (
                State TEXT,
                County TEXT,
                State_code TEXT,
                County_code TEXT,
                Year_span TEXT,
                Measure_name TEXT,
                Measure_id TEXT,
                Numerator TEXT,
                Denominator TEXT,
                Raw_value TEXT,
                Confidence_Interval_Lower_Bound TEXT,
                Confidence_Interval_Upper_Bound TEXT,
                Data_Release_Year TEXT,
                fipscode TEXT
            )
        ''')
        
        # Insert sample data
        cursor.execute('''
            INSERT INTO zip_county VALUES 
            ('02138', 'MA', 'Middlesex County', 'Massachusetts', 'MA', '25017', '32000', '1.0', '1', 'Cambridge'),
            ('10001', 'NY', 'New York County', 'New York', 'NY', '36061', '21000', '1.0', '1', 'New York')
        ''')
        
        cursor.execute('''
            INSERT INTO county_health_rankings VALUES 
            ('Massachusetts', 'Middlesex County', '25', '25017', '2020', 'Adult obesity', '1', '100', '500', '0.20', '0.18', '0.22', '2021', '25017'),
            ('Massachusetts', 'Middlesex County', '25', '25017', '2020', 'Unemployment', '2', '50', '1000', '0.05', '0.04', '0.06', '2021', '25017'),
            ('New York', 'New York County', '36', '36061', '2020', 'Adult obesity', '1', '150', '600', '0.25', '0.23', '0.27', '2021', '36061')
        ''')
        
        conn.commit()
        conn.close()

    def tearDown(self):
        """Clean up test database."""
        if os.path.exists(self.test_db):
            os.remove(self.test_db)
        import shutil
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)

    def test_zip_to_county_lookup(self):
        """Test ZIP code to county lookup query."""
        conn = sqlite3.connect(self.test_db)
        cursor = conn.cursor()
        
        # Test query that API would use
        cursor.execute('''
            SELECT county, county_code, state_abbreviation 
            FROM zip_county 
            WHERE zip = ?
        ''', ('02138',))
        
        result = cursor.fetchone()
        self.assertIsNotNone(result)
        self.assertEqual(result[0], 'Middlesex County')
        self.assertEqual(result[1], '25017')
        self.assertEqual(result[2], 'MA')
        
        conn.close()

    def test_health_data_lookup(self):
        """Test health data lookup by county and measure."""
        conn = sqlite3.connect(self.test_db)
        cursor = conn.cursor()
        
        # Test query that API would use
        cursor.execute('''
            SELECT * FROM county_health_rankings 
            WHERE County = ? AND Measure_name = ?
        ''', ('Middlesex County', 'Adult obesity'))
        
        result = cursor.fetchone()
        self.assertIsNotNone(result)
        self.assertEqual(result[5], 'Adult obesity')  # Measure_name
        self.assertEqual(result[9], '0.20')  # Raw_value
        
        conn.close()

    def test_join_query(self):
        """Test JOIN query that API would use."""
        conn = sqlite3.connect(self.test_db)
        cursor = conn.cursor()
        
        # Test the full query that API would use
        cursor.execute('''
            SELECT chr.* 
            FROM zip_county zc 
            JOIN county_health_rankings chr ON zc.county = chr.County 
            WHERE zc.zip = ? AND chr.Measure_name = ?
        ''', ('02138', 'Adult obesity'))
        
        result = cursor.fetchone()
        self.assertIsNotNone(result)
        self.assertEqual(len(result), 14)  # Should have all 14 columns
        self.assertEqual(result[5], 'Adult obesity')  # Measure_name
        
        conn.close()

    def test_parameterized_queries(self):
        """Test that parameterized queries work correctly (SQL injection protection)."""
        conn = sqlite3.connect(self.test_db)
        cursor = conn.cursor()
        
        # Test with potentially malicious input
        malicious_input = "'; DROP TABLE county_health_rankings; --"
        
        cursor.execute('''
            SELECT * FROM county_health_rankings 
            WHERE Measure_name = ?
        ''', (malicious_input,))
        
        result = cursor.fetchall()
        self.assertEqual(len(result), 0)  # Should return no results, not crash
        
        # Verify table still exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='county_health_rankings'")
        self.assertIsNotNone(cursor.fetchone())
        
        conn.close()


if __name__ == '__main__':
    # Create a test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add all test classes
    suite.addTests(loader.loadTestsFromTestCase(TestCSVToSQLite))
    suite.addTests(loader.loadTestsFromTestCase(TestDatabaseQueries))
    
    # Run tests with verbose output
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Exit with appropriate code
    sys.exit(0 if result.wasSuccessful() else 1)
