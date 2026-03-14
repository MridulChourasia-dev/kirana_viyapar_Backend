# API Test Suite - Quick Reference

## Installation
```bash
pip install -r tests/requirements.txt
```

## Basic Commands

### Run All Tests
```bash
pytest tests/ -v
```

### Run by Module
```bash
pytest tests/test_auth.py -v          # Auth only
pytest tests/test_customers.py -v     # Customers only
pytest tests/test_products.py -v      # Products only
pytest tests/test_invoices.py -v      # Invoices only
pytest tests/test_payments.py -v      # Payments only
pytest tests/test_reports.py -v       # Reports only
```

### Run by Marker
```bash
pytest -m auth -v                 # Marker: auth
pytest -m customers -v            # Marker: customers
pytest -m negative -v             # Marker: negative tests
pytest -m "auth or customers" -v  # Multiple markers
```

### Run Specific Test
```bash
pytest tests/test_auth.py::test_login_user_success -v
```

### Search by Name
```bash
pytest tests/ -k "create" -v      # Tests with "create" in name
pytest tests/ -k "customer" -v    # Tests with "customer" in name
```

---

## Output & Reporting

### Verbose Output
```bash
pytest tests/ -v                  # Normal verbose
pytest tests/ -vv                 # Extra verbose (more details)
pytest tests/ -v -s               # With print statements
```

### Coverage Report
```bash
pytest tests/ --cov=app --cov-report=html
# Open: htmlcov/index.html
```

### HTML Report
```bash
pytest tests/ -v --html=report.html --self-contained-html
# Open: report.html
```

### Slowest Tests
```bash
pytest tests/ -v --durations=10   # Show 10 slowest tests
```

---

## Debugging

### Stop on First Failure
```bash
pytest tests/ -v -x
```

### Show Failure Details
```bash
pytest tests/test_name.py::test_function -v --tb=short
pytest tests/test_name.py::test_function -v --tb=long
```

### Drop into Debugger
```bash
pytest tests/ --pdb               # On failure
pytest tests/ --pdbcls=IPython.terminal.debugger:Pdb
```

### Collect Only (No Execution)
```bash
pytest tests/ --collect-only
```

---

## Performance

### Parallel Execution
```bash
pip install pytest-xdist
pytest tests/ -v -n auto          # All CPU cores
pytest tests/ -v -n 4             # 4 workers
```

### Run Tests Multiple Times
```bash
pytest tests/ -v --count=5        # Run 5 times
```

### Watch Tests (Auto-rerun on Change)
```bash
pip install pytest-watch
ptw tests/                         # Watch all tests
ptw tests/test_customers.py       # Watch specific file
```

---

## Using Make

```bash
make install              # Install dependencies
make test                 # Run all tests
make test-auth            # Run auth tests
make test-customers       # Run customer tests
make test-coverage        # Generate coverage
make test-html            # Generate HTML report
make test-negative        # Run negative tests
make help                 # Show all commands
```

---

## Common Use Cases

### Before Committing Code
```bash
pytest tests/ -v --cov=app
```

### Testing New Feature
```bash
pytest tests/test_customers.py -v -k "create" -s
```

### Debugging Failed Test
```bash
pytest tests/test_customers.py::test_name -vv -s
```

### Quick Smoke Test
```bash
pytest tests/test_auth.py tests/test_customers.py -v --maxfail=1
```

### Generate Report for Team
```bash
pytest tests/ --html=report.html --cov=app --cov-report=html
```

---

## Status Codes Cheatsheet

| Code | Meaning | Common Test |
|------|---------|-------------|
| 200 | OK | GET, PATCH |
| 201 | Created | POST |
| 204 | No Content | DELETE |
| 400 | Bad Request | Invalid payload |
| 401 | Unauthorized | No/invalid token |
| 403 | Forbidden | Insufficient permissions |
| 404 | Not Found | Non-existent resource |
| 409 | Conflict | Duplicate entry |
| 422 | Unprocessable | Validation failed |
| 500 | Server Error | Backend issue |

---

## Test Data Reference

### Test User
- Email: `test.user.<random>@example.com` (auto-generated)
- Password: `TestPassword123!`
- Business: Auto-created

### Sample Customer
```python
{
    "name": "Rajesh Kumar",
    "email": "rajesh@example.com",
    "phone": "+919876543210",
    "gstin": "29ABCDE1234F1Z5",
    "city": "Mumbai"
}
```

### Sample Product
```python
{
    "name": "Wireless Mouse",
    "sku": "SKU-001",
    "sale_price": 599.00,
    "purchase_price": 350.00,
    "stock_quantity": 100,
    "tax_rate": 18.0
}
```

### Sample Invoice
```python
{
    "customer_id": "uuid",
    "items": [
        {
            "product_id": "uuid",
            "quantity": 1,
            "unit_price": 599.00,
            "tax_rate": 18
        }
    ]
}
```

---

## Backend Commands

### Start Backend
```bash
docker compose up --build -d
```

### Stop Backend
```bash
docker compose down
```

### View Logs
```bash
docker compose logs -f viyapar-backend
docker compose logs -f viyapar-db
```

### Reset Database
```bash
docker compose down -v           # Remove volumes
docker compose up --build -d     # Restart
```

### Direct Database Access
```bash
docker exec viyapar-db psql -U viyapar -d viyapar
```

---

## Environment Variables

In `conftest.py`:
```python
BASE_URL = "http://localhost:8000/api/v1"
TIMEOUT = 30.0
TEST_USER_EMAIL = "test.user.<random>@example.com"
TEST_USER_PASSWORD = "TestPassword123!"
```

---

## Markers Available

```python
@pytest.mark.auth        # Auth tests
@pytest.mark.customers   # Customer tests
@pytest.mark.products    # Product tests
@pytest.mark.invoices    # Invoice tests
@pytest.mark.payments    # Payment tests
@pytest.mark.reports     # Report tests
@pytest.mark.negative    # Error/negative tests
@pytest.mark.asyncio     # Async tests
```

Usage: `pytest -m auth -v`

---

## Fixtures Available

From `conftest.py`:

```python
@pytest.fixture
async def http_client()              # Unauthenticated client

@pytest.fixture
async def authenticated_client()     # Client with bearer token

@pytest.fixture
async def test_customer()            # Pre-created customer

@pytest.fixture
async def test_product()             # Pre-created product

@pytest.fixture
async def test_customer_and_product()  # Both for invoices
```

---

## Quick Test Recipe

```bash
# 1. Install
pip install -r tests/requirements.txt

# 2. Start backend
docker compose up --build -d

# 3. Run tests
pytest tests/ -v

# 4. View report
pytest tests/ --html=report.html --self-contained-html
open report.html

# 5. Generate coverage
pytest tests/ --cov=app --cov-report=html
open htmlcov/index.html
```

---

## Tips & Tricks

### Run only passing tests from last run
```bash
pytest tests/ -v --lf
```

### Run failed tests first
```bash
pytest tests/ -v --ff
```

### Run tests matching pattern
```bash
pytest tests/ -k "not negative" -v  # Exclude negative tests
pytest tests/ -k "customer and create" -v  # Customer create tests
```

### Run with minimum verbosity
```bash
pytest tests/
```

### Show local variables on failure
```bash
pytest tests/ -v -l
```

### Custom pytest options
```bash
# In pytest.ini or command line:
pytest tests/ -v --tb=short --strict-markers
```

---

## System Requirements

- Python 3.10+
- pip or conda
- Docker & Docker Compose (for containerized backend)
- 2GB RAM minimum
- 500MB disk space

---

**Quick Help**: `pytest --help`  
**Detailed Guide**: See `TEST_EXECUTION_GUIDE.md`  
**Main README**: See `README.md`
