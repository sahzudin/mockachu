# Mockachu - Mock Data Generator | Fake Data Generator | Test Data Generator

🎲 **Free Open Source Mock Data Generator** - A powerful desktop application and REST API for generating realistic fake data, test data, and sample data for testing, development, and prototyping.

**Keywords**: mock data generator, fake data generator, test data generator, sample data, dummy data, random data generator, API testing data, database seed data, JSON generator, CSV generator

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue.svg)](https://python.org)
[![License](https://img.shields.io/badge/License-Open%20Source-green.svg)](#license)
[![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20macOS%20%7C%20Linux-lightgrey.svg)](#installation)
[![REST API](https://img.shields.io/badge/REST%20API-Available-orange.svg)](#rest-api)

---

## What is Mockachu?

Mockachu is a **free, open-source mock data generator** that helps developers, testers, and data analysts create realistic test data quickly and efficiently. Whether you need fake user profiles, sample financial data, or dummy API responses, Mockachu generates high-quality mock data in multiple formats.

### Perfect for:
- 🧪 **API Testing** - Generate sample data for REST API development and testing
- 🏗️ **Database Seeding** - Create realistic data to populate development databases  
- 📊 **Data Analysis** - Generate datasets for testing analytics and reporting tools
- 🎯 **Prototyping** - Create sample data for demos and proof-of-concepts
- 🚀 **Development** - Mock external API responses during development
- 📱 **Mobile App Testing** - Generate user profiles and content for mobile apps

## 🚀 Key Features & Capabilities

### 🖥️ Desktop Application (GUI)
- **User-Friendly Interface** - Cross-platform desktop app with intuitive PyQt6 GUI
- **15+ Data Generators** - Generate realistic data for:
  - 👥 **Personal Data**: Names, emails, addresses, phone numbers, ages
  - 💳 **Financial Data**: Credit cards, IBANs, currencies, bank information
  - 🌍 **Geographic Data**: Cities, countries, coordinates, timezones
  - 🚗 **Automotive Data**: Car brands, models, VIN numbers
  - 🎨 **Design Data**: Colors (hex, RGB, names), HTML color codes
  - 🎬 **Entertainment**: Movies, TV series, random text content
  - 💻 **Technical Data**: UUIDs, IP addresses, MAC addresses, domains, URLs
  - 📅 **Date & Time**: Timestamps, date ranges, custom formats
  - � **Numeric Data**: Random numbers, sequences, decimal values
- **Multiple Export Formats** - JSON, CSV, XML, SQL, HTML output
- **Advanced Customization** - Configure nullable fields, custom patterns, parameters
- **Configuration Management** - Save, load, and share field configurations

### 🌐 REST API for Developers
- **RESTful HTTP API** - Generate mock data programmatically via HTTP requests
- **Easy Integration** - Simple JSON-based API calls for any programming language
- **Interactive Documentation** - Built-in Swagger UI at `/swagger` for API testing
- **High Performance** - Generate up to 100,000 rows per request
- **CORS Enabled** - Cross-origin requests supported for web applications
- **Multiple Response Formats** - Return data as JSON, CSV, or XML
- **No Authentication Required** - Perfect for development and testing environments

---

## 💡 Popular Use Cases & Examples

### For Developers
- **API Development**: Generate sample user profiles, orders, products for REST API testing
- **Database Seeding**: Create realistic test data for MySQL, PostgreSQL, MongoDB databases
- **Unit Testing**: Generate mock objects and test fixtures for automated testing
- **Frontend Development**: Create placeholder content for React, Vue, Angular applications
- **Microservices Testing**: Generate data for testing service integrations

### For QA Engineers & Testers
- **Load Testing**: Generate large datasets for performance testing with JMeter, K6
- **Test Data Management**: Create consistent test data across different environments
- **Automation Testing**: Generate dynamic test data for Selenium, Cypress tests
- **API Testing**: Create varied request payloads for Postman, Insomnia testing
- **Edge Case Testing**: Generate boundary values and edge cases for thorough testing

### For Data Analysts & Scientists
- **Data Pipeline Testing**: Create sample datasets for ETL process validation
- **Analytics Development**: Generate data for testing reports, dashboards, visualizations
- **Machine Learning**: Create training datasets for ML model development
- **Data Modeling**: Generate sample data for database schema validation
- **A/B Testing**: Create consistent test datasets for experiment analysis

### Common Search Terms This Tool Helps With:
`mock data generator`, `fake data generator`, `test data generator`, `dummy data creator`, `sample data generator`, `random user generator`, `JSON data generator`, `CSV test data`, `API mock data`, `database seed data`, `lorem ipsum generator`, `fake person generator`, `random address generator`, `credit card number generator`, `phone number generator`, `email generator`, `UUID generator`, `timestamp generator`

---

## 📦 Installation

### Pre-built Executables (No Python Required)

For users who prefer standalone applications without installing Python:

> ⚠️ **Security Note**: Pre-built executables will show security warnings on first run because they're not code-signed. This is normal and safe. See the [Security Information](#-security-information) section below for details on how to bypass these warnings.

#### Download Links
- **Windows**: Download `Mockachu-Windows.zip` from [Releases](https://github.com/sahzudin/mockachu/releases)
- **macOS**: Download `Mockachu-macOS.zip` from [Releases](https://github.com/sahzudin/mockachu/releases)
- **Linux**: Download `Mockachu-Linux.tar.gz` from [Releases](https://github.com/sahzudin/mockachu/releases)

#### Installation Instructions

**Windows:**
1. Download and extract `Mockachu-Windows.zip`
2. Run `Mockachu.exe`
3. No installation required!

**macOS:**
1. Download and extract `Mockachu-macOS.zip`
2. Move `Mockachu.app` to your Applications folder
3. Right-click and select "Open" (required for first run due to Gatekeeper)

**Linux:**
1. Download and extract `Mockachu-Linux.tar.gz`
2. Make executable: `chmod +x mockdatagenerator`
3. Run: `./mockdatagenerator`

> **Note**: Pre-built executables include both the GUI application and the API server. Use command-line flags to choose which component to run.

### From PyPI (Recommended for Developers)

```bash
# Install API only (lightweight)
pip install mockachu

# Install with GUI support
pip install mockachu[gui]

# Install with development tools
pip install mockachu[dev]

# Install everything
pip install mockachu[all]
```

### From Source

```bash
git clone https://github.com/sahzudin/mockachu.git
cd mockachu
pip install -e ".[gui,dev]"
```

## 🔒 Security Information

### Pre-built Executable Security Warnings

When running pre-built executables, you may encounter security warnings. This is normal and expected for unsigned applications:

#### macOS
**Warning**: "macOS cannot verify the app is free of malware"

**Solutions**:
1. **Right-click method** (Recommended):
   - Right-click the app → Select "Open"
   - Click "Open" in the security dialog
   
2. **System Preferences method**:
   - Go to System Preferences → Security & Privacy
   - Click "Open Anyway" for Mockachu
   
3. **Terminal method**:
   ```bash
   xattr -d com.apple.quarantine /path/to/Mockachu.app
   ```

#### Windows
**Warning**: "Windows protected your PC" or SmartScreen filter

**Solution**:
- Click "More info" → "Run anyway"
- Or go to Settings → Update & Security → Windows Security → App & browser control

#### Linux
**Issue**: Downloaded file may not be executable

**Solution**:
```bash
chmod +x mockdatagenerator
```

### Why These Warnings Occur

- **Code Signing Cost**: Apple Developer ($99/year) and Windows certificates ($200-400/year)
- **Open Source**: This project prioritizes accessibility over commercial code signing
- **False Positive**: The warnings don't indicate actual malware - just lack of expensive certificates

### Alternative: Run from Source
If you prefer to avoid security warnings entirely:
```bash
git clone https://github.com/sahzudin/mockachu.git
cd mockachu
pip install -e ".[gui]"
python app.py
```

## Quick Start

### Desktop Application

1. **Install with GUI support**
   ```bash
   pip install mockachu[gui]
   ```

2. **Run the Application**
   ```bash
   mockachu
   # or
   python app.py
   ```

### API Server

1. **Install the package**
   ```bash
   pip install mockachu
   ```

2. **Start the API Server**
   ```bash
   mock-data-api
   # or
   python api_server.py
   ```
   
   Or with custom options:
   ```bash
   python api_server.py --host 0.0.0.0 --port 8000 --debug
   ```

3. **Access API Documentation**
   ```
   http://localhost:8843/docs
   ```

## API Documentation

### Base URL
```
http://localhost:8843
```

### Authentication
No authentication required for local development.

---

### 🔍 **GET /** - API Information
Get basic API information and available endpoints.

**Response:**
```json
{
  "name": "Mockachu API",
  "version": "1.0.0",
  "description": "REST API for generating realistic mock data",
  "endpoints": {
    "GET /": "API information",
    "GET /health": "Health check",
    "GET /generators": "List available generators and actions",
    "POST /generate": "Generate mock data",
    "GET /docs": "API documentation"
  },
  "documentation": "/docs"
}
```

---

### 💚 **GET /health** - Health Check
Check if the API server is running properly.

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2025-08-16T10:30:00.000Z",
  "version": "1.0.0"
}
```

---

### 🛠️ **GET /generators** - Available Generators
Get a list of all available generators and their actions.

**Response:**
```json
{
  "generators": [
    {
      "name": "PERSON_GENERATOR",
      "display_name": "Persons",
      "actions": [
        {
          "name": "RANDOM_FIRST_NAME",
          "display_name": "First name"
        },
        {
          "name": "RANDOM_LAST_NAME", 
          "display_name": "Last name"
        }
      ]
    }
  ]
}
```

---

### 🎲 **POST /generate** - Generate Mock Data
Generate mock data based on field configuration.

**Content-Type:** `application/json`

**Request Body:**
```json
{
  "fields": [
    {
      "name": "field_name",
      "generator": "GENERATOR_NAME", 
      "action": "ACTION_NAME",
      "nullable_percentage": 0,
      "parameters": []
    }
  ],
  "rows": 10,
  "format": "JSON"
}
```

**Parameters:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `fields` | Array | ✅ | Array of field configurations |
| `fields[].name` | String | ✅ | Field name in output |
| `fields[].generator` | String | ✅ | Generator to use (see `/generators`) |
| `fields[].action` | String | ✅ | Action to perform (see `/generators`) |
| `fields[].nullable_percentage` | Number | ❌ | Percentage of null values (0-100) |
| `fields[].parameters` | Array | ❌ | Additional parameters for the action (can contain numbers, strings, etc.) |
| `rows` | Number | ❌ | Number of rows to generate (default: 10, max: 100,000) |
| `format` | String | ❌ | Output format: `JSON`, `CSV`, `XML` (default: JSON) |

**Response:**
```json
{
  "success": true,
  "data": [
    {
      "first_name": "John",
      "email": "john.doe@example.com"
    }
  ],
  "metadata": {
    "rows_generated": 1,
    "fields_count": 2,
    "format": "JSON",
    "generation_time_seconds": 0.045,
    "timestamp": "2025-08-16T10:30:00.000Z"
  }
}
```

---

## API Examples

### Basic Person Data
```bash
curl -X POST http://localhost:8843/generate \\
  -H "Content-Type: application/json" \\
  -d '{
    "fields": [
      {
        "name": "first_name",
        "generator": "PERSON_GENERATOR",
        "action": "RANDOM_FIRST_NAME"
      },
      {
        "name": "last_name", 
        "generator": "PERSON_GENERATOR",
        "action": "RANDOM_LAST_NAME"
      },
      {
        "name": "email",
        "generator": "IT_GENERATOR",
        "action": "RANDOM_EMAIL"
      }
    ],
    "rows": 5
  }'
```

### Numbers with Parameters
```bash
curl -X POST http://localhost:8843/generate \\
  -H "Content-Type: application/json" \\
  -d '{
    "fields": [
      {
        "name": "user_id",
        "generator": "STRING_GENERATOR",
        "action": "RANDOM_NUMBER",
        "parameters": [1000, 9999]
      },
      {
        "name": "price",
        "generator": "STRING_GENERATOR", 
        "action": "RANDOM_DECIMAL_NUMBER",
        "parameters": [10.0, 1000.0, 2]
      }
    ],
    "rows": 3,
    "format": "CSV"
  }'
```

### Geographic Data with Patterns
```bash
curl -X POST http://localhost:8843/generate \\
  -H "Content-Type: application/json" \\
  -d '{
    "fields": [
      {
        "name": "location",
        "generator": "GEO_GENERATOR",
        "action": "RANDOM_GEO_DATA_PATTERN",
        "parameters": ["{city}, {country}"]
      },
      {
        "name": "phone",
        "generator": "IT_GENERATOR",
        "action": "RANDOM_PHONE_NUMBER", 
        "parameters": ["+1-___-___-____"]
      }
    ],
    "rows": 10
  }'
```

### Currency and Financial Data
```bash
curl -X POST http://localhost:8843/generate \\
  -H "Content-Type: application/json" \\
  -d '{
    "fields": [
      {
        "name": "currency_info",
        "generator": "MONEY_GENERATOR",
        "action": "RANDOM_CURRENCY_PATTERN",
        "parameters": ["{currency} ({code})"]
      },
      {
        "name": "credit_card",
        "generator": "MONEY_GENERATOR",
        "action": "RANDOM_CREDIT_CARD_NUMBER"
      },
      {
        "name": "iban",
        "generator": "MONEY_GENERATOR", 
        "action": "RANDOM_IBAN"
      }
    ],
    "rows": 5
  }'
```

---

## Available Generators

| Generator | Description | Example Actions |
|-----------|-------------|-----------------|
| `PERSON_GENERATOR` | Personal data | `RANDOM_FIRST_NAME`, `RANDOM_LAST_NAME`, `RANDOM_AGE` |
| `IT_GENERATOR` | IT-related data | `RANDOM_EMAIL`, `RANDOM_IPV4`, `RANDOM_PHONE_NUMBER` |
| `GEO_GENERATOR` | Geographic data | `RANDOM_CITY`, `RANDOM_COUNTRY`, `RANDOM_COORDINATES` |
| `MONEY_GENERATOR` | Financial data | `RANDOM_CURRENCY`, `RANDOM_CREDIT_CARD_NUMBER`, `RANDOM_IBAN` |
| `CAR_GENERATOR` | Automotive data | `RANDOM_CAR_BRAND`, `RANDOM_CAR_MODEL`, `RANDOM_CAR_VIN` |
| `COLOR_GENERATOR` | Color data | `RANDOM_COMMON_COLOR`, `RANDOM_HTML_COLOR_HEX` |
| `STRING_GENERATOR` | Text and numbers | `RANDOM_WORD`, `RANDOM_NUMBER`, `RANDOM_DECIMAL_NUMBER` |
| `CALENDAR_GENERATOR` | Date and time | `RANDOM_DATE`, `RANDOM_TIME`, `RANDOM_DATE_TIME` |
| `BIOLOGY_GENERATOR` | Biological data | `RANDOM_ANIMAL`, `RANDOM_PLANT` |
| `CINEMA_GENERATOR` | Entertainment | `RANDOM_MOVIE`, `RANDOM_SERIES` |
| `FILE_GENERATOR` | File-related | `RANDOM_FILE_NAME`, `RANDOM_FILE_EXTENSION` |
| `YES_NO_GENERATOR` | Boolean values | `YES`, `NO`, `RANDOM_BOOLEAN` |
| `SEQUENCE_GENERATOR` | Sequential data | `SEQUENTIAL_NUMBER` |
| `CUSTOM_LIST_GENERATOR` | Custom lists | `RANDOM_CUSTOM_LIST_ITEM` |
| `FIELD_BUILDER_GENERATOR` | Field combinations | `FIELD_JOIN` |

For a complete list of actions and parameters, use the `/generators` endpoint.

---

## Error Handling

The API returns appropriate HTTP status codes and error messages:

### 400 Bad Request
```json
{
  "error": "Missing required field: 'fields'"
}
```

### 500 Internal Server Error
```json
{
  "error": "Generation failed: Invalid generator configuration"
}
```

---

## Limits

- **Maximum rows per request:** 100,000
- **Maximum fields per request:** 50
- **Request timeout:** 30 seconds
- **No rate limiting** (development server)

---

## Python Client Example

```python
import requests

# Initialize API client
api_url = "http://localhost:8843"

def generate_mock_data(fields, rows=10, format="JSON"):
    """Generate mock data using the API"""
    payload = {
        "fields": fields,
        "rows": rows,
        "format": format
    }
    
    response = requests.post(f"{api_url}/generate", json=payload)
    
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"API Error: {response.text}")

# Example usage
fields = [
    {
        "name": "user_id",
        "generator": "STRING_GENERATOR",
        "action": "RANDOM_NUMBER",
        "parameters": [1000, 9999]
    },
    {
        "name": "username",
        "generator": "IT_GENERATOR", 
        "action": "RANDOM_USERNAME"
    },
    {
        "name": "email",
        "generator": "IT_GENERATOR",
        "action": "RANDOM_EMAIL"
    }
]

result = generate_mock_data(fields, rows=100)
print(f"Generated {len(result['data'])} records")
```

---

## JavaScript/Node.js Client Example

```javascript
const axios = require('axios');

async function generateMockData(fields, rows = 10, format = 'JSON') {
  try {
    const response = await axios.post('http://localhost:8843/generate', {
      fields: fields,
      rows: rows,
      format: format
    });
    
    return response.data;
  } catch (error) {
    throw new Error(`API Error: ${error.response?.data?.error || error.message}`);
  }
}

// Example usage
const fields = [
  {
    name: 'product_name',
    generator: 'STRING_GENERATOR',
    action: 'RANDOM_WORD'
  },
  {
    name: 'price',
    generator: 'STRING_GENERATOR',
    action: 'RANDOM_DECIMAL_NUMBER',
    parameters: [10.0, 1000.0, 2]
  },
  {
    name: 'currency',
    generator: 'MONEY_GENERATOR',
    action: 'RANDOM_CURRENCY_CODE'
  }
];

generateMockData(fields, 50)
  .then(result => {
    console.log(`Generated ${result.data.length} records`);
    console.log(result.data.slice(0, 3)); // Show first 3 records
  })
  .catch(error => console.error(error));
```

---

## Development

### Running Tests
```bash
# Start the API server
python api_server.py

# In another terminal, run tests
python test_api.py
```

### Production Deployment
For production use, deploy with a proper WSGI server like Gunicorn:

```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:8000 api_server:app
```

---

## Developer Notes

**About the Developer**: I'm primarily a C# and Java developer who codes Python as a hobby. This project represents my exploration into Python development.

**AI-Generated Code**: Most of this codebase has been generated with AI assistance. While thoroughly tested, there may be bugs or non-idiomatic Python patterns. Contributions and improvements are welcome!

**Code Quality**: As this is a hobby project with AI-generated components, please review code carefully before using in production environments. Feel free to submit issues or pull requests for any improvements.

---

## 🤔 Frequently Asked Questions (FAQ)

### Q: How to generate fake user data for testing?
**A:** Use the `PERSON_GENERATOR` with actions like `RANDOM_PERSON_FIRST_NAME`, `RANDOM_PERSON_LAST_NAME`, and `RANDOM_EMAIL` to create realistic user profiles.

### Q: Can I generate test data for databases?
**A:** Yes! Export data in SQL format or use JSON/CSV to import into MySQL, PostgreSQL, MongoDB, or any database.

### Q: How to create mock API responses?
**A:** Use the REST API endpoints to generate JSON data that matches your API schema requirements.

### Q: Is this free to use commercially?
**A:** Yes, this is open source software free for both personal and commercial use.

### Q: How to generate credit card numbers for testing?
**A:** Use `MONEY_GENERATOR` with `RANDOM_CREDIT_CARD_NUMBER` action. Note: These are fake numbers for testing only.

### Q: Can I generate addresses and phone numbers?
**A:** Yes, use `GEO_GENERATOR` for addresses and `IT_GENERATOR` for phone numbers with custom patterns.

### Q: How to generate large datasets?
**A:** The API supports up to 100,000 rows per request. For larger datasets, make multiple requests.

### Q: Does it work with Postman/Insomnia?
**A:** Yes! Use the REST API endpoints in any HTTP client. Check `/swagger` for interactive documentation.

---

## 🏷️ Tags & Keywords

**Mock Data Generator**, **Fake Data Generator**, **Test Data Generator**, **Random Data Generator**, **Sample Data Creator**, **Dummy Data Generator**, **API Testing Tool**, **Database Seeding Tool**, **JSON Generator**, **CSV Generator**, **Python Mock Data**, **REST API Testing**, **Test Data Management**, **QA Testing Tool**, **Development Tool**, **Data Generation API**, **Faker Alternative**, **Mock Server**, **Test Fixtures Generator**

---

## License

This project is open source. Feel free to use it for your development and testing needs.

---

## Support

For issues, feature requests, or questions:
- Create an issue in the repository
- Check the API documentation at `/docs`
- Test endpoints using the provided examples
