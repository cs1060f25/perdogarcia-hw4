# CS1060 Homework 4 - API Prototyping with Generative AI

## Assignment Overview
Create a CSV to SQLite converter and a REST API endpoint for county health data. Due: September 29, 9 PM ET.

## Part 1: Data Processing (15 points)

Task:
Use generative AI to create a Python 3 script called csv_to_sqlite.py.

It should accept valid CSV files with a header row of field names (these should be valid SQL column names, with no escaping or spaces).
Behavior on bad CSV is undefined.
On valid inputs, it should output a sqlite3 database called data.db.
sqlite3 works on Windows, Mac, and Linux.
Your script should take two arguments: the name of your sqlite3 database and the name of the CSV file.
💡 Using GPT-4o in the Harvard Sandbox, this task took course staff 15 minutes, with one prompt and one change. The AI output SQL commands with column names in quotes instead of bare SQL, which needed to be altered. Your prompt and model may well get it right the first time.


Checklist:

- [x] Create `csv_to_sqlite.py` script ✅ **VERIFIED** by `test/run_tests.py` - Script exists and functional
- [x] Script accepts 2 arguments: database name and CSV file name ✅ **VERIFIED** by `test/test_csv_to_sqlite.py::test_invalid_arguments`
- [x] Converts CSV with headers to SQLite database table ✅ **VERIFIED** by `test/test_csv_to_sqlite.py::test_basic_functionality`
- [x] Uses filename (without extension) as table name ✅ **VERIFIED** by `test/test_csv_to_sqlite.py::test_zip_county_structure`
- [x] All columns created as TEXT type ✅ **VERIFIED** by `test/test_csv_to_sqlite.py::test_basic_functionality` - All columns are TEXT
- [x] Handles command line arguments properly ✅ **VERIFIED** by `test/test_csv_to_sqlite.py::test_invalid_arguments`
- [x] Includes error handling for missing files ✅ **VERIFIED** by `test/test_csv_to_sqlite.py::test_missing_csv_file`
- [x] Add attribution comment for AI-generated code ✅ **VERIFIED** by inspection of `csv_to_sqlite.py` header

Here is an example of how you might implement a basic test for your script.

cat$ rm data.db
cat$ python3 csv_to_sqlite.py data.db zip_county.csv
cat$ python3 csv_to_sqlite.py data.db county_health_rankings.csv
cat$ sqlite3 data.db
SQLite version 3.39.5 2022-10-14 20:58:05
Enter ".help" for usage hints.
sqlite> .schema zip_county
CREATE TABLE zip_county (zip TEXT, default_state TEXT, county TEXT, county_state TEXT,
    state_abbreviation TEXT, county_code TEXT, zip_pop TEXT, zip_pop_in_county TEXT,
    n_counties TEXT, default_city TEXT);
sqlite> select count(*) from zip_county;
54553
sqlite> .schema county_health_rankings
CREATE TABLE county_health_rankings (state TEXT, county TEXT, state_code TEXT,
    county_code TEXT, year_span TEXT, measure_name TEXT, measure_id TEXT, numerator TEXT,
    denominator TEXT, raw_value TEXT, confidence_interval_lower_bound TEXT,
    confidence_interval_upper_bound TEXT, data_release_year TEXT, fipscode TEXT);
sqlite> select count(*) from county_health_rankings;
303864
sqlite> .q


## Part 2: API Prototype (35 points) - 🔲 TODO

Task:
Create an API prototype with a county_data endpoint that uses the data.db you generated in Part 1, and host it on your choice of platforms—Netlify, Vercel, Render, Bolt, Lovable, ... they're all fine.

You can use the cs1060-hw2-baseLinks to an external site. example from HW2 as a way to easily get started deploying to Vercel. If you choose to use Vercel on a free/hobby plan, keep in mind you'll have to copy it to your own private GitHub instead of the cs1060f25 organization, and copy/clone that repo into the cs1060 organization for submission.

Here is one way to test an API endpoint:

cat$ curl -H'content-type:application/json' \
  -d'{"input": "five", "inputType": "text", "outputType": "decimal"}' \
  https://cat-hw2-render.onrender.com/convert
This should yield the following output:

{"error":null,"result":"5"}


### 2.1 Setup and Configuration
- [x] Choose deployment platform (Vercel/Netlify/Render/etc.)
- [x] Set up project structure for chosen platform
- [x] Create requirements.txt if needed
- [x] Set up database integration (copy data.db or recreate)

### 2.2 API Implementation
- [x] Create `/county_data` endpoint that accepts POST requests
- [x] Implement JSON input/output handling with `content-type: application/json`
- [x] Required input validation:
  - [x] `zip` (required): 5-digit ZIP code
  - [x] `measure_name` (required): must be one of the specified health measures
- [x] Special case: Return HTTP 418 if `coffee=teapot` is in POST data
- [x] Error handling:
  - [x] 400 (Bad Request) if zip or measure_name missing
  - [x] 404 (Not Found) for non-existent zip/measure_name pairs
  - [x] 404 (Not Found) for endpoints other than county_data

### 2.3 Database Query Logic
- [x] Join zip_county and county_health_rankings tables
- [x] Query logic: zip → county → health data for specific measure
- [x] SQL injection protection (parameterized queries)
- [x] Return all matching records in county_health_rankings schema format

### 2.4 Valid Health Measures (for validation)
Implement validation for these exact strings:
- [x] "Violent crime rate" ✅ **VERIFIED** by `test/test_api_endpoints.py::test_valid_health_measures`
- [x] "Unemployment" ✅ **VERIFIED** by `test/test_api_endpoints.py::test_valid_health_measures`
- [x] "Children in poverty" ✅ **VERIFIED** by `test/test_api_endpoints.py::test_valid_health_measures`
- [x] "Diabetic screening" ✅ **VERIFIED** by `test/test_api_endpoints.py::test_valid_health_measures`
- [x] "Mammography screening" ✅ **VERIFIED** by `test/test_api_endpoints.py::test_valid_health_measures`
- [x] "Preventable hospital stays" ✅ **VERIFIED** by `test/test_api_endpoints.py::test_valid_health_measures`
- [x] "Uninsured" ✅ **VERIFIED** by `test/test_api_endpoints.py::test_valid_health_measures`
- [x] "Sexually transmitted infections" ✅ **VERIFIED** by `test/test_api_endpoints.py::test_valid_health_measures`
- [x] "Physical inactivity" ✅ **VERIFIED** by `test/test_api_endpoints.py::test_valid_health_measures`
- [x] "Adult obesity" ✅ **VERIFIED** by `test/test_api_endpoints.py::test_valid_health_measures`
- [x] "Premature Death" ✅ **VERIFIED** by `test/test_api_endpoints.py::test_valid_health_measures`
- [x] "Daily fine particulate matter" ✅ **VERIFIED** by `test/test_api_endpoints.py::test_valid_health_measures`

### 2.5 Output Format
Ensure JSON output matches county_health_rankings schema:
- [x] confidence_interval_lower_bound ✅ **VERIFIED** by `test/test_api_endpoints.py::test_output_format_schema`
- [x] confidence_interval_upper_bound ✅ **VERIFIED** by `test/test_api_endpoints.py::test_output_format_schema`
- [x] county ✅ **VERIFIED** by `test/test_api_endpoints.py::test_output_format_schema`
- [x] county_code ✅ **VERIFIED** by `test/test_api_endpoints.py::test_output_format_schema`
- [x] data_release_year ✅ **VERIFIED** by `test/test_api_endpoints.py::test_output_format_schema`
- [x] denominator ✅ **VERIFIED** by `test/test_api_endpoints.py::test_output_format_schema`
- [x] fipscode ✅ **VERIFIED** by `test/test_api_endpoints.py::test_output_format_schema`
- [x] measure_id ✅ **VERIFIED** by `test/test_api_endpoints.py::test_output_format_schema`
- [x] measure_name ✅ **VERIFIED** by `test/test_api_endpoints.py::test_output_format_schema`
- [x] numerator ✅ **VERIFIED** by `test/test_api_endpoints.py::test_output_format_schema`
- [x] raw_value ✅ **VERIFIED** by `test/test_api_endpoints.py::test_output_format_schema`
- [x] state ✅ **VERIFIED** by `test/test_api_endpoints.py::test_output_format_schema`
- [x] state_code ✅ **VERIFIED** by `test/test_api_endpoints.py::test_output_format_schema`
- [x] year_span ✅ **VERIFIED** by `test/test_api_endpoints.py::test_output_format_schema`

## Part 3: Deployment and Testing - 🔲 TODO

### 3.1 Deploy API
- [ ] Deploy to chosen platform
- [ ] Ensure database is accessible in production
- [ ] Test endpoint is publicly accessible
- [ ] Verify POST requests work (browsers send GET by default)

### 3.2 Testing
Test these scenarios:
- [x] Valid request: `{"zip":"02138","measure_name":"Adult obesity"}` ✅ **VERIFIED** by `test/test_specific_scenarios.py::test_scenario_valid_request` - Returns 7 records
- [x] Missing zip: `{"measure_name":"Adult obesity"}` → 400 ✅ **VERIFIED** by `test/test_specific_scenarios.py::test_scenario_missing_zip`
- [x] Missing measure_name: `{"zip":"02138"}` → 400 ✅ **VERIFIED** by `test/test_specific_scenarios.py::test_scenario_missing_measure_name`
- [x] Invalid zip: `{"zip":"00000","measure_name":"Adult obesity"}` → 404 ✅ **VERIFIED** by `test/test_specific_scenarios.py::test_scenario_invalid_zip`
- [x] Invalid measure_name: `{"zip":"02138","measure_name":"Invalid"}` → 404 ✅ **VERIFIED** by `test/test_specific_scenarios.py::test_scenario_invalid_measure_name`
- [x] Coffee teapot: `{"zip":"02138","measure_name":"Adult obesity","coffee":"teapot"}` → 418 ✅ **VERIFIED** by `test/test_specific_scenarios.py::test_scenario_coffee_teapot`
- [x] Wrong endpoint: GET/POST to `/other` → 404 ✅ **VERIFIED** by `test/test_specific_scenarios.py::test_scenario_wrong_endpoint_*`
- [x] SQL injection attempt (for security) ✅ **VERIFIED** by `test/test_specific_scenarios.py::test_scenario_sql_injection_attempts` - All attempts safely handled

## Part 4: Repository Setup - 🔲 TODO

### 4.1 Required Files
- [ ] `./link.txt` - Contains only the API endpoint URL
- [ ] `./csv_to_sqlite.py` - The converter script (already done)
- [ ] `./requirements.txt` - Python dependencies (if any)
- [ ] `./README.md` - Project documentation
- [ ] `./.gitignore` - Prevent caches, use Python gitignore template
- [ ] Additional platform-specific files (vercel.json, etc.)

### 4.2 Repository Management
- [ ] Create private repo in cs1060f25 organization: `<username>-hw4`
- [ ] Ensure repository matches deployed code exactly
- [ ] Commit all required files
- [ ] Test repository can be cloned fresh and scripts work

## Part 5: Final Verification - 🔲 TODO

### 5.1 End-to-End Testing
- [ ] Fresh directory test: clone repo and run csv_to_sqlite.py
- [ ] Verify data.db is created correctly with both CSV files
- [ ] Test API endpoint from link.txt works
- [ ] Verify all error codes work correctly
- [ ] Test with different CSV files to ensure script is generic

### 5.2 Submission Checklist
- [ ] Repository is private in cs1060f25 organization
- [ ] Repository name follows `<username>-hw4` format
- [ ] link.txt contains working API endpoint URL (no query string)
- [ ] All required files present and working
- [ ] API handles all specified test cases correctly
- [ ] SQL injection protection implemented

## Technical Notes
- Use SQLite database created by csv_to_sqlite.py
- Join tables: zip_county (zip → county info) + county_health_rankings (county → health data)
- Deployment platforms: Vercel/Netlify/Render all acceptable
- Security: Must sanitize SQL inputs to prevent injection attacks
- Testing: Use curl or Postman for POST requests (not browser)

## Grading Criteria
- Automated testing of csv_to_sqlite.py script
- API functionality testing via link.txt endpoint
- Error handling and HTTP status codes
- SQL injection resistance testing
- Repository structure and completeness