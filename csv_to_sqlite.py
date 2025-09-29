#!/usr/bin/env python3
"""
CSV to SQLite Converter

Author: Pedro Garcia
Sources:
- Database code: Claude AI (Anthropic)
- CSV parsing: Python standard library documentation
"""

import sys
import csv
import sqlite3
import os
from typing import List, Dict, Any, Optional


def validate_args() -> tuple[str, str]:
    """Validate command line arguments.

    Returns:
        tuple: (database_name, csv_file) if valid

    Raises:
        SystemExit: If arguments are invalid
    """
    if len(sys.argv) != 3:
        print("Usage: python3 csv_to_sqlite.py <database_name> <csv_file>", file=sys.stderr)
        sys.exit(1)

    database_name = sys.argv[1]
    csv_file = sys.argv[2]

    if not os.path.exists(csv_file):
        print(f"Error: CSV file '{csv_file}' not found", file=sys.stderr)
        sys.exit(1)

    return database_name, csv_file


def get_table_name(csv_file: str) -> str:
    """Extract table name from CSV filename.

    Args:
        csv_file (str): Path to CSV file

    Returns:
        str: Table name (filename without extension)
    """
    filename = os.path.basename(csv_file)
    # Handle .csv and .CSV extensions
    if filename.lower().endswith('.csv'):
        return filename[:-4]
    return filename


def create_table_from_csv(database_name: str, csv_file: str) -> None:
    """Create SQLite table from CSV file.

    Args:
        database_name (str): Name of SQLite database file
        csv_file (str): Path to CSV file

    Raises:
        SystemExit: If database or CSV operations fail
    """
    table_name = get_table_name(csv_file)

    try:
        # Read CSV file properly using csv.reader to handle embedded newlines
        with open(csv_file, 'r', encoding='utf-8-sig', newline='') as f:
            # Use csv.reader to properly handle quoted fields with newlines
            csv_reader = csv.reader(f)

            # Get headers from first row
            try:
                headers = next(csv_reader)
            except StopIteration:
                raise ValueError("CSV file is empty")

            # Read all data rows
            data_rows = list(csv_reader)

        # Use DictReader for proper field mapping
        with open(csv_file, 'r', encoding='utf-8-sig', newline='') as f:
            reader = csv.DictReader(f)

        # Clean headers for SQL (remove quotes, spaces, and BOM)
        clean_headers = []
        for i, header in enumerate(headers):
            # Remove quotes and clean up column names
            clean_header = header.strip().strip('"').strip("'")
            # Remove BOM (Byte Order Mark) if present
            if clean_header.startswith('\ufeff'):
                clean_header = clean_header[1:]
            if not clean_header:
                clean_header = f'column_{i}'
            clean_headers.append(clean_header)

        # Check if there are any data rows
        if len(data_rows) == 0:
            print(f"Warning: CSV file '{csv_file}' contains only headers, creating empty table")

        # Connect to database
        conn = sqlite3.connect(database_name)
        conn.row_factory = sqlite3.Row  # Enable column access by name
        cursor = conn.cursor()

        # Create table with appropriate column types
        columns_def = []
        for header in clean_headers:
            # For zip_county table, ensure zip is TEXT to preserve leading zeros
            if table_name == 'zip_county' and header.lower() == 'zip':
                columns_def.append(f'"{header}" TEXT')
            # For other columns, use TEXT by default
            else:
                columns_def.append(f'"{header}" TEXT')

        # Drop table if it exists to avoid duplicates
        cursor.execute(f'DROP TABLE IF EXISTS "{table_name}"')

        # Create the table
        create_table_sql = f'CREATE TABLE "{table_name}" ({', '.join(columns_def)})'
        cursor.execute(create_table_sql)

        # Insert data
        # Insert data row by row
        placeholders = ', '.join(['?'] * len(clean_headers))
        columns = ', '.join(f'"{col}"' for col in clean_headers)
        insert_sql = f'INSERT INTO "{table_name}" ({columns}) VALUES ({placeholders})'

        # Process each data row
        row_count = 0
        for row_data in data_rows:
            # Skip empty rows
            if not any(field.strip() for field in row_data):
                continue

            # Clean the row data (row_data is already parsed by csv.reader)
            row = [str(cell).strip('\"\' ') for cell in row_data]

            # Ensure we have the right number of columns
            if len(row) < len(clean_headers):
                # Pad with empty strings if row is too short
                row += [''] * (len(clean_headers) - len(row))
            elif len(row) > len(clean_headers):
                # Truncate if row is too long
                row = row[:len(clean_headers)]

            # Clean the ZIP code if this is the zip_county table
            if table_name == 'zip_county' and len(row) > 0:
                row[0] = row[0].strip('\"\'')

            try:
                cursor.execute(insert_sql, row)
                row_count += 1
            except sqlite3.Error as e:
                print(f"Error inserting row: {e}")
                print(f"Row data: {row}")
                raise

        # Create indexes for faster lookups
        if table_name == 'zip_county':
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_zip_county_zip ON zip_county("zip")')
        elif table_name == 'county_health_rankings':
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_health_county_state ON county_health_rankings(County_code, Measure_name)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_health_measure ON county_health_rankings(Measure_name)')

        conn.commit()
        conn.close()

        print(f"Successfully created table '{table_name}' in database '{database_name}'")

    except sqlite3.Error as e:
        print(f"Database error: {e}", file=sys.stderr)
        if 'conn' in locals():
            conn.rollback()
            conn.close()
        sys.exit(1)
    except csv.Error as e:
        print(f"CSV error in {csv_file}: {e}", file=sys.stderr)
        if 'conn' in locals():
            conn.rollback()
            conn.close()
        sys.exit(1)
    except IOError as e:
        print(f"File I/O error: {e}", file=sys.stderr)
        if 'conn' in locals():
            conn.rollback()
            conn.close()
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr)
        if 'conn' in locals():
            conn.rollback()
            conn.close()
        sys.exit(1)


def main() -> None:
    """Main function to convert CSV to SQLite.

    This script reads a CSV file and creates a corresponding SQLite table with the same data.
    The table name is derived from the CSV filename.

    Usage:
        python3 csv_to_sqlite.py <database_name> <csv_file>

    Example:
        python3 csv_to_sqlite.py data.db my_data.csv

    Exits with status code 0 on success, 1 on error.
    """
    try:
        database_name, csv_file = validate_args()
        create_table_from_csv(database_name, csv_file)
        sys.exit(0)
    except KeyboardInterrupt:
        print("\nOperation cancelled by user", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
