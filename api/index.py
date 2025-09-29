"""
County Health Data API

Author: Pedro Garcia
Sources:
- Database code: Claude AI (Anthropic)
- Flask patterns: Official Flask docs
"""

from flask import Flask, request, jsonify
import sqlite3
import os
import sys

app = Flask(__name__)

# Valid health measures for validation
VALID_MEASURES = {
    "Violent crime rate", "Unemployment", "Children in poverty",
    "Diabetic screening", "Mammography screening", "Preventable hospital stays",
    "Uninsured", "Sexually transmitted infections", "Physical inactivity",
    "Adult obesity", "Premature Death", "Daily fine particulate matter"
}

def validate_zip(zip_code: str) -> bool:
    """Validate ZIP code format.

    Args:
        zip_code (str): ZIP code to validate

    Returns:
        bool: True if valid 5-digit ZIP code
    """
    return zip_code.isdigit() and len(zip_code) == 5

def validate_measure(measure: str) -> bool:
    """Validate measure name.

    Args:
        measure (str): Measure name to validate

    Returns:
        bool: True if valid measure name
    """
    return measure in VALID_MEASURES

def get_database_path() -> str:
    """Get the path to the database file.

    Returns:
        str: Path to data.db file
    """
    # DEPLOYMENT_MODE: Multiple path strategies for different environments
    
    # Strategy 1: Same directory as this file (Vercel serverless)
    current_dir = os.path.dirname(os.path.abspath(__file__))
    local_db = os.path.join(current_dir, 'data.db')
    
    # Strategy 2: Relative to current working directory
    cwd_db = os.path.join(os.getcwd(), 'data.db')
    
    # Strategy 3: Parent directory (local development)
    parent_dir = os.path.dirname(current_dir)
    parent_db = os.path.join(parent_dir, 'data.db')
    
    # Strategy 4: Check common Vercel paths
    vercel_paths = [
        '/var/task/api/data.db',
        '/tmp/data.db',
        './api/data.db',
        './data.db'
    ]
    
    # Try each path in order
    all_paths = [local_db, cwd_db, parent_db] + vercel_paths
    
    for db_path in all_paths:
        if os.path.exists(db_path):
            print(f"Found database at: {db_path}")
            return db_path
    
    # If no database found, log all attempted paths
    print("Database not found. Attempted paths:")
    for i, path in enumerate(all_paths, 1):
        exists = "EXISTS" if os.path.exists(path) else "NOT FOUND"
        print(f"  {i}. {path} - {exists}")
    
    print(f"Current working directory: {os.getcwd()}")
    print(f"Script directory: {current_dir}")
    print(f"Directory contents: {os.listdir(current_dir) if os.path.exists(current_dir) else 'N/A'}")
    
    # Return the most likely path even if it doesn't exist (for better error messages)
    return local_db

def query_county_health_data(zip_code: str, measure_name: str) -> list:
    """Query county health data for given ZIP code and measure.

    Args:
        zip_code (str): 5-digit ZIP code
        measure_name (str): Health measure name

    Returns:
        list: List of matching health data records

    Raises:
        sqlite3.Error: If database query fails
    """
    db_path = get_database_path()

    if not os.path.exists(db_path):
        raise FileNotFoundError(f"Database file not found: {db_path}")

    print(f"Database path: {db_path}")
    print(f"Querying for zip: {zip_code}, measure: {measure_name}")

    try:
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row  # Enable column access by name
        cursor = conn.cursor()

        # First, get the county_code for the zip code
        # Note: The zip column is defined with quotes in the schema
        zip_query = """
        SELECT county_code
        FROM zip_county
        WHERE "zip" = ?
        LIMIT 1
        """

        print(f"Executing zip query: {zip_query} with zip: {zip_code}")
        cursor.execute(zip_query, (zip_code,))
        zip_result = cursor.fetchone()

        if not zip_result:
            print(f"No county found for zip code: {zip_code}")
            return []

        fips_code = zip_result['county_code']
        print(f"Found FIPS code: {fips_code} for zip: {zip_code}")

        # Now query the health data using fipscode join
        query = """
        SELECT
            State as state,
            County as county,
            State_code as state_code,
            County_code as county_code,
            Year_span as year_span,
            Measure_name as measure_name,
            Measure_id as measure_id,
            Numerator as numerator,
            Denominator as denominator,
            Raw_value as raw_value,
            Confidence_Interval_Lower_Bound as confidence_interval_lower_bound,
            Confidence_Interval_Upper_Bound as confidence_interval_upper_bound,
            Data_Release_Year as data_release_year,
            fipscode as fipscode
        FROM county_health_rankings
        WHERE fipscode = ?
          AND Measure_name = ?
        """

        print(f"Executing health data query with fipscode: {fips_code}, measure: {measure_name}")
        cursor.execute(query, (fips_code, measure_name))
        results = cursor.fetchall()

        print(f"Found {len(results)} matching records")

        # Convert rows to dictionaries
        data = []
        for row in results:
            data.append({
                'state': row['state'],
                'county': row['county'],
                'state_code': row['state_code'],
                'county_code': row['county_code'],
                'year_span': row['year_span'],
                'measure_name': row['measure_name'],
                'measure_id': row['measure_id'],
                'numerator': row['numerator'],
                'denominator': row['denominator'],
                'raw_value': row['raw_value'],
                'confidence_interval_lower_bound': row['confidence_interval_lower_bound'],
                'confidence_interval_upper_bound': row['confidence_interval_upper_bound'],
                'data_release_year': row['data_release_year'],
                'fipscode': row['fipscode']
            })

        return data

    except sqlite3.Error as e:
        print(f"SQLite error: {e}")
        raise
    except Exception as e:
        print(f"Unexpected error: {e}")
        raise
    finally:
        if 'conn' in locals():
            conn.close()

@app.route('/county_data', methods=['POST'])
def county_data():
    """Handle county health data requests.

    Returns:
        JSON response with health data or error message
    """
    try:
        # Check for coffee=teapot parameter (HTTP 418)
        if request.json and 'coffee' in request.json and request.json['coffee'] == 'teapot':
            return jsonify({"error": "I'm a teapot", "status": 418}), 418

        # Validate request has JSON content
        if not request.json:
            return jsonify({"error": "Request must contain JSON data", "status": 400}), 400

        # Extract and validate required parameters
        zip_code = request.json.get('zip')
        measure_name = request.json.get('measure_name')

        # Check for missing parameters
        if not zip_code:
            return jsonify({"error": "Missing required parameter: zip", "status": 400}), 400

        if not measure_name:
            return jsonify({"error": "Missing required parameter: measure_name", "status": 400}), 400

        # Validate ZIP code format
        if not validate_zip(zip_code):
            return jsonify({"error": "Invalid zip code format. Must be 5 digits.", "status": 404}), 404

        # Validate measure name
        if not validate_measure(measure_name):
            return jsonify({"error": "Invalid measure_name", "status": 404}), 404

        # Query database
        try:
            results = query_county_health_data(zip_code, measure_name)
        except FileNotFoundError as e:
            return jsonify({"error": "Database not found", "status": 500}), 500
        except sqlite3.Error as e:
            return jsonify({"error": "Database error", "status": 500}), 500

        # Check if any results found
        if not results:
            return jsonify({"error": "No data found for the given zip code and measure", "status": 404}), 404

        # Return successful results
        return jsonify(results), 200

    except Exception as e:
        return jsonify({"error": "Internal server error", "status": 500}), 500

@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors for wrong endpoints or methods."""
    return jsonify({"error": "Endpoint not found", "status": 404}), 404

@app.errorhandler(405)
def method_not_allowed(error):
    """Handle 405 errors for wrong HTTP methods."""
    return jsonify({"error": "Method not allowed", "status": 404}), 404

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5005)