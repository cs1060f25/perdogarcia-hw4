# Bug Report for csv_to_sqlite.py

## Summary
The test suite revealed several critical bugs in `csv_to_sqlite.py` that need to be fixed for proper functionality and to meet the CS1060 HW4 requirements.

## Critical Bugs Found

### 1. **BOM (Byte Order Mark) Handling Issue** 🚨 **CRITICAL**
**Location:** Lines 71-94 (CSV reading and header processing)
**Problem:** The CSV files contain a BOM character at the start, causing the first column to be named `"﻿zip"` instead of `"zip"`.
**Impact:** API queries will fail because they can't find the `zip` column.
**Evidence:** 
```sql
-- Current (broken):
CREATE TABLE "zip_country" ("﻿zip" TEXT, ...)
-- Expected:
CREATE TABLE "zip_country" ("zip" TEXT, ...)
```

### 2. **Duplicate sys.exit(1) Statement** 
**Location:** Lines 223-224
**Problem:** 
```python
sys.exit(1)
sys.exit(1)  # Duplicate line
```
**Impact:** Code duplication, potential confusion.

### 3. **Print Statement Inside Loop**
**Location:** Line 160
**Problem:** Success message prints for every row instead of once at the end.
**Current behavior:** 
```
Successfully inserted 1 rows into zip_country
Successfully inserted 2 rows into zip_country
Successfully inserted 3 rows into zip_country
...
```
**Expected:** Single message at the end.

### 4. **Wrong Table Name in Index Creation**
**Location:** Line 165
**Problem:** 
```python
elif table_name == 'country_health_rankings':  # Wrong name
```
**Should be:** 
```python
elif table_name == 'county_health_rankings':  # Correct name
```
**Impact:** Indexes won't be created for the health rankings table.

### 5. **Incorrect Column Names in Index Creation**
**Location:** Lines 166-167
**Problem:** Index references columns that may not exist due to case sensitivity.
**Current:**
```python
cursor.execute('CREATE INDEX ... ON country_health_rankings(County, State_code)')
```
**Issue:** Column names might have different casing in actual CSV.

## Test Results
- **14 tests run**
- **2 failures, 1 error**
- **Critical issues prevent proper API functionality**

### Failed Tests:
1. `test_zip_county_structure` - Can't find zip column due to BOM
2. `test_special_characters_in_data` - Extra row due to print statement bug
3. `test_real_data_integration` - Column name mismatch due to BOM

## Recommended Fixes

### Fix 1: BOM Handling
**Location:** Line 71 (file reading)
**Current:**
```python
with open(csv_file, 'r', encoding='utf-8') as f:
    content = f.read()
```
**Fix:**
```python
with open(csv_file, 'r', encoding='utf-8-sig') as f:  # utf-8-sig removes BOM
    content = f.read()
```

### Fix 2: Remove Duplicate sys.exit()
**Location:** Line 224
**Fix:** Delete the duplicate line.

### Fix 3: Move Print Statement Outside Loop
**Location:** Line 160
**Current:**
```python
print(f"Successfully inserted {row_count} rows into {table_name}")  # Inside loop
```
**Fix:** Move this line to after the loop (around line 161).

### Fix 4: Correct Table Name
**Location:** Line 165
**Current:**
```python
elif table_name == 'country_health_rankings':
```
**Fix:**
```python
elif table_name == 'county_health_rankings':
```

### Fix 5: Use Actual Column Names for Indexes
**Location:** Lines 166-167
**Fix:** Use the actual column names from the CSV headers instead of hardcoded names.

## Additional Improvements Recommended

### 1. Better Error Handling for BOM
Add explicit BOM detection and removal:
```python
def clean_header(header):
    """Clean header by removing BOM and quotes."""
    # Remove BOM character if present
    if header.startswith('\ufeff'):
        header = header[1:]
    return header.strip().strip('"').strip("'")
```

### 2. Validate Column Names
Ensure column names are valid SQL identifiers.

### 3. Better Index Strategy
Create indexes based on actual column names found in the CSV.

## Impact on API
These bugs will cause the API to fail because:
1. ZIP lookups won't work (wrong column name due to BOM)
2. Health data queries may fail (missing indexes)
3. JOIN queries between tables will fail

## Testing
The comprehensive test suite in `test/test_csv_to_sqlite.py` can verify all fixes work correctly.

## Priority
**HIGH** - These bugs must be fixed before the API can function properly for CS1060 HW4 submission.
