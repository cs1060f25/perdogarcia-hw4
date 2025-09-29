#!/usr/bin/env python3
"""
Deployment Preparation Script

Author: Pedro Garcia
Prepares the project for deployment by:
1. Ensuring data.db exists and is up to date
2. Copying database to api/ directory for serverless deployment
3. Updating link.txt with deployment URL (after deployment)
"""

import os
import shutil
import subprocess
import sys
from pathlib import Path

def ensure_database_exists():
    """Ensure data.db exists and is up to date."""
    project_root = Path(__file__).parent
    db_path = project_root / 'data.db'
    zip_csv = project_root / 'zip_county.csv'
    health_csv = project_root / 'county_health_rankings.csv'
    script_path = project_root / 'csv_to_sqlite.py'
    
    print("🔍 Checking database...")
    
    if not db_path.exists():
        print("❌ data.db not found. Creating database...")
        create_database = True
    else:
        # Check if CSV files are newer than database
        db_mtime = db_path.stat().st_mtime
        csv_mtime = max(zip_csv.stat().st_mtime, health_csv.stat().st_mtime)
        
        if csv_mtime > db_mtime:
            print("⚠️  CSV files are newer than database. Recreating...")
            create_database = True
        else:
            print("✅ Database is up to date")
            create_database = False
    
    if create_database:
        # Remove old database
        if db_path.exists():
            db_path.unlink()
        
        # Create new database
        print("📊 Converting zip_county.csv...")
        result = subprocess.run([
            sys.executable, str(script_path), str(db_path), str(zip_csv)
        ], capture_output=True, text=True)
        
        if result.returncode != 0:
            print(f"❌ Failed to convert zip_county.csv: {result.stderr}")
            return False
        
        print("📊 Converting county_health_rankings.csv...")
        result = subprocess.run([
            sys.executable, str(script_path), str(db_path), str(health_csv)
        ], capture_output=True, text=True)
        
        if result.returncode != 0:
            print(f"❌ Failed to convert county_health_rankings.csv: {result.stderr}")
            return False
        
        print("✅ Database created successfully")
    
    return True

def copy_database_for_deployment():
    """Copy database to api/ directory for serverless deployment."""
    project_root = Path(__file__).parent
    source_db = project_root / 'data.db'
    dest_db = project_root / 'api' / 'data.db'
    
    if not source_db.exists():
        print("❌ Source database not found")
        return False
    
    print("📋 Copying database to api/ directory...")
    shutil.copy2(source_db, dest_db)
    
    # Verify copy
    if dest_db.exists():
        print("✅ Database copied successfully")
        return True
    else:
        print("❌ Failed to copy database")
        return False

def update_api_for_deployment():
    """Update API to use local database in serverless environment."""
    api_file = Path(__file__).parent / 'api' / 'index.py'
    
    # Read the current file
    with open(api_file, 'r') as f:
        content = f.read()
    
    # Check if already updated for deployment
    if 'DEPLOYMENT_MODE' in content:
        print("✅ API already configured for deployment")
        return True
    
    print("🔧 Updating API for deployment...")
    
    # Replace the get_database_path function
    old_function = '''def get_database_path() -> str:
    """Get the path to the database file.

    Returns:
        str: Path to data.db file
    """
    # Look for data.db in the parent directory (project root)
    parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    db_path = os.path.join(parent_dir, 'data.db')
    return db_path'''
    
    new_function = '''def get_database_path() -> str:
    """Get the path to the database file.

    Returns:
        str: Path to data.db file
    """
    # DEPLOYMENT_MODE: Check for database in same directory first (serverless)
    current_dir = os.path.dirname(os.path.abspath(__file__))
    local_db = os.path.join(current_dir, 'data.db')
    
    if os.path.exists(local_db):
        return local_db
    
    # Fallback to parent directory (local development)
    parent_dir = os.path.dirname(current_dir)
    db_path = os.path.join(parent_dir, 'data.db')
    return db_path'''
    
    # Replace the function
    updated_content = content.replace(old_function, new_function)
    
    # Write back to file
    with open(api_file, 'w') as f:
        f.write(updated_content)
    
    print("✅ API updated for deployment")
    return True

def verify_deployment_ready():
    """Verify that everything is ready for deployment."""
    project_root = Path(__file__).parent
    
    required_files = [
        'api/index.py',
        'api/data.db',
        'vercel.json',
        'requirements.txt'
    ]
    
    print("🔍 Verifying deployment readiness...")
    
    for file_path in required_files:
        full_path = project_root / file_path
        if full_path.exists():
            print(f"✅ {file_path}")
        else:
            print(f"❌ {file_path} - MISSING")
            return False
    
    # Check database size
    db_path = project_root / 'api' / 'data.db'
    db_size = db_path.stat().st_size / (1024 * 1024)  # MB
    print(f"📊 Database size: {db_size:.1f} MB")
    
    if db_size > 100:
        print("⚠️  Warning: Database is quite large for serverless deployment")
    
    print("🚀 Ready for deployment!")
    return True

def main():
    """Main deployment preparation process."""
    print("=" * 60)
    print("DEPLOYMENT PREPARATION")
    print("=" * 60)
    
    steps = [
        ("Ensure database exists", ensure_database_exists),
        ("Copy database for deployment", copy_database_for_deployment),
        ("Update API for deployment", update_api_for_deployment),
        ("Verify deployment readiness", verify_deployment_ready)
    ]
    
    for step_name, step_func in steps:
        print(f"\n📋 {step_name}...")
        if not step_func():
            print(f"❌ Failed: {step_name}")
            return False
    
    print("\n" + "=" * 60)
    print("✅ DEPLOYMENT PREPARATION COMPLETE!")
    print("=" * 60)
    print("\n📝 Next steps:")
    print("1. Deploy to Vercel: vercel --prod")
    print("2. Update link.txt with the deployment URL")
    print("3. Test the deployed API")
    
    return True

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
