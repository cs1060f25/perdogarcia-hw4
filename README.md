# CS1060 HW4 - County Health Data API

**Author:** Pedro Garcia
**Course:** CS1060 Fall 2025
**Assignment:** Homework 4 - API Prototyping with Generative AI
**GitHub: User** PerdoGarcia

A Flask-based REST API that provides county health data by ZIP code and health measures, deployed on Vercel with automatic database creation from CSV sources.

## 📋 Project Overview

This project implements a production-ready API that:
- Converts CSV health data to SQLite database
- Provides REST endpoint for querying health data by ZIP code
- Includes comprehensive security measures (SQL injection protection)
- Supports all 12 required health measures
- Deployed on Vercel with automatic scaling

## 🚀 Live API

**Endpoint:** https://perdogarcia-hw4.vercel.app/county_data

## 📁 Project Structure

```
perdogarcia-hw4/
├── api/
│   ├── index.py              # Main Flask API application
│   ├── templates/            # HTML templates (if needed)
│   └── __init__.py          # Package initialization
├── test/                     # Comprehensive test suite
│   ├── test_api_endpoints.py # API functionality tests
│   ├── test_csv_to_sqlite.py # CSV converter tests
│   ├── test_sql_injection_attacks.py # Security tests
│   └── run_tests.py         # Test runner
├── csv_to_sqlite.py         # CSV to SQLite converter
├── requirements.txt         # Python dependencies
├── vercel.json             # Vercel deployment config
├── link.txt                # API endpoint URL
├── .gitignore              # Git ignore rules
└── README.md               # This file
```

## 🛠️ Setup & Installation

### Prerequisites
- Python 3.8+
- pip package manager

### Local Development

1. **Clone the repository:**
```bash
git clone <repository-url>
cd perdogarcia-hw4
```

2. **Install dependencies:**
```bash
pip install -r requirements.txt
```

3. **Create the database:**
```bash
python3 csv_to_sqlite.py data.db zip_county.csv
python3 csv_to_sqlite.py data.db county_health_rankings.csv
```

4. **Run the API locally:**
```bash
python3 api/index.py
```

The API will be available at `http://localhost:5005`
or https://perdogarcia-hw4.vercel.app


## 📊 Data Sources

This project uses two public health datasets:

1. **ZIP Code to County Mapping**
   - Source: RowZero (based on public datasets)
   - File: `zip_county.csv`
   - Records: ~54,553 ZIP codes

2. **County Health Rankings**
   - Source: County Health Rankings & Roadmaps
   - File: `county_health_rankings.csv`
   - Records: ~303,864 health measurements

## 🔌 API Usage

### Endpoint: `POST /county_data`

**Request Format:**
```bash
curl -X POST https://perdogarcia-hw4.vercel.app/county_data \
  -H "Content-Type: application/json" \
  -d '{"zip":"02138","measure_name":"Adult obesity"}'
```

**Required Parameters:**
- `zip`: 5-digit ZIP code (string)
- `measure_name`: Health measure name (see valid measures below)

**Valid Health Measures:**
- Violent crime rate
- Unemployment
- Children in poverty
- Diabetic screening
- Mammography screening
- Preventable hospital stays
- Uninsured
- Sexually transmitted infections
- Physical inactivity
- Adult obesity
- Premature Death
- Daily fine particulate matter

### Response Format

**Success (200):**
```json
[
  {
    "confidence_interval_lower_bound": "0.22",
    "confidence_interval_upper_bound": "0.24",
    "county": "Middlesex County",
    "county_code": "17",
    "data_release_year": "2012",
    "denominator": "263078",
    "fipscode": "25017",
    "measure_id": "11",
    "measure_name": "Adult obesity",
    "numerator": "60771.02",
    "raw_value": "0.23",
    "state": "MA",
    "state_code": "25",
    "year_span": "2009"
  }
]
```

**Error Responses:**
- `400`: Missing required parameters
- `404`: Invalid ZIP code or measure name
- `418`: Coffee teapot easter egg (`{"coffee":"teapot"}`)

### Example Requests

**Valid Request:**
```bash
curl -X POST https://perdogarcia-hw4.vercel.app/county_data \
  -H "Content-Type: application/json" \
  -d '{"zip":"10001","measure_name":"Unemployment"}'
```

**Missing Parameter (400):**
```bash
curl -X POST https://perdogarcia-hw4.vercel.app/county_data \
  -H "Content-Type: application/json" \
  -d '{"zip":"02138"}'
```

**Coffee Teapot (418):**
```bash
curl -X POST https://perdogarcia-hw4.vercel.app/county_data \
  -H "Content-Type: application/json" \
  -d '{"zip":"02138","measure_name":"Adult obesity","coffee":"teapot"}'
```

## 🧪 Testing

The project includes comprehensive test suites:

### Run All Tests
```bash
python3 test/run_tests.py
```

### Individual Test Suites
```bash
# API functionality tests
python3 test/test_api_endpoints.py

# CSV converter tests
python3 test/test_csv_to_sqlite.py

# Security tests (SQL injection)
python3 test/test_sql_injection_attacks.py
```

### Test Coverage
- ✅ **66 total tests**
- ✅ **API functionality** (23 tests)
- ✅ **CSV processing** (14 tests)
- ✅ **SQL injection security** (21 tests)
- ✅ **Production deployment** (8 tests)

## 🔒 Security Features

- **SQL Injection Protection**: All queries use parameterized statements
- **Input Validation**: ZIP codes and measure names are validated
- **Error Handling**: No sensitive information leaked in error messages
- **Whitelist Validation**: Only approved health measures accepted

## 🚀 Deployment

The API is deployed on **Vercel** with:
- Automatic scaling
- Global CDN
- HTTPS by default
- Serverless functions
- Database created on-demand from CSV files

### Deployment Configuration

The project uses `vercel.json` for deployment settings and automatically:
1. Detects the production environment
2. Creates the SQLite database from CSV files in `/tmp/`
3. Handles all requests through the Flask application

## 🛠️ CSV to SQLite Converter

The `csv_to_sqlite.py` script converts any CSV file to SQLite:

**Usage:**
```bash
python3 csv_to_sqlite.py <database_name> <csv_file>
```

**Features:**
- Handles BOM (Byte Order Mark) in CSV files
- Preserves leading zeros in ZIP codes
- Creates appropriate indexes
- Supports embedded newlines in CSV fields
- Generic implementation for any CSV structure

**Example:**
```bash
python3 csv_to_sqlite.py data.db my_data.csv
```

## 📈 Performance

- **Response Time**: ~150ms average
- **Database Size**: 49.2MB (compressed in deployment)
- **Concurrent Requests**: Handled by Vercel's serverless infrastructure
- **Uptime**: 99.9% (Vercel SLA)

## 🤖 AI Attribution

This project was developed with assistance from generative AI:

**AI Tools Used:**
- Claude AI (Anthropic) - Database code, Flask patterns
- GitHub Copilot - Code completion and suggestions

**Human Contributions:**
- Project architecture and design
- Security implementation and testing
- Deployment configuration and optimization
- Comprehensive test suite development

## 📝 Assignment Requirements Checklist

- ✅ **Part 1: Data Processing (15 points)**
  - ✅ `csv_to_sqlite.py` script created
  - ✅ Accepts database name and CSV file arguments
  - ✅ Outputs SQLite database with proper schema
  - ✅ Works with provided CSV files and arbitrary CSV files

- ✅ **Part 2: API Prototype (35 points)**
  - ✅ `/county_data` endpoint implemented
  - ✅ Accepts POST requests with JSON
  - ✅ Returns data in county_health_rankings schema
  - ✅ Validates ZIP codes (5 digits) and measure names
  - ✅ Implements all required HTTP status codes (200, 400, 404, 418)
  - ✅ SQL injection protection with parameterized queries
  - ✅ Deployed on Vercel platform

- ✅ **Submission Requirements**
  - ✅ `./link.txt` - API endpoint URL
  - ✅ `./csv_to_sqlite.py` - CSV converter script
  - ✅ `./requirements.txt` - Python dependencies
  - ✅ `./README.md` - This documentation
  - ✅ `./.gitignore` - Git ignore rules

## 📞 Support

For questions or issues:
1. Check the test suite for examples
2. Review the API documentation above
3. Test locally before deployment

## 📄 License

This project is submitted as coursework for CS1060 Fall 2025.
