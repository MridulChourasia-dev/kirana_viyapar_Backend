# API Test Execution Guide

## Environment Setup

### Prerequisites
- Python 3.10+
- Docker and Docker Compose (if using containerized backend)
- pip package manager

### Step 1: Install Test Dependencies

```bash
cd tests
pip install -r requirements.txt
```

Or if using conda:
```bash
conda install pytest httpx pytest-asyncio
```

### Step 2: Start the Backend

Using Docker Compose:
```bash
# From project root
docker compose up --build -d

# Verify containers are running
docker compose ps

# Check logs
docker compose logs -f viyapar-backend
```

Using local Python:
```bash
cd backend
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Step 3: Verify Backend is Ready

```bash
curl http://localhost:8000/docs
```

You should see Swagger UI. API is ready when you see the interactive documentation.

---

## Running Tests

### Quick Start (Run Everything)

```bash
cd tests
pytest -v
```

Expected output:
```
============================== test session starts ==============================
collected 80 items

test_auth.py::test_register_user_success PASSED                           [  1%]
test_auth.py::test_login_user_success PASSED                              [  2%]
...
============================== 80 passed in 12.34s ==============================
```

### Run by Module

```bash
# Authentication tests
pytest tests/test_auth.py -v

# Customer CRUD tests
pytest tests/test_customers.py -v

# Product management tests
pytest tests/test_products.py -v

# Invoice management tests
pytest tests/test_invoices.py -v

# Payment tracking tests
pytest tests/test_payments.py -v

# Report generation tests
pytest tests/test_reports.py -v
```

### Run by Marker/Category

```bash
# Auth tests only
pytest -m auth -v

# Customer tests only
pytest -m customers -v

# All business logic tests (exclude negative)
pytest -m "not negative" -v

# Negative/error tests only
pytest -m negative -v

# Multiple categories
pytest -m "auth or customers" -v
```

### Run Specific Tests

```bash
# Single test
pytest tests/test_auth.py::test_login_user_success -v

# Multiple specific tests
pytest tests/test_customers.py::test_create_customer_success \
         tests/test_customers.py::test_list_customers_success -v

# Tests matching pattern
pytest tests/ -k "create" -v
pytest tests/ -k "pagination" -v
```

### Using Make (Convenience)

```bash
# Install dependencies
make install

# Run all tests
make test

# Run specific module
make test-customers
make test-invoices

# With coverage
make test-coverage

# With HTML report
make test-html

# Show help
make help
```

---

## Test Output Interpretation

### ✅ Passed Test
```
test_auth.py::test_login_user_success PASSED                           [  1%]
```
- Green indicator
- Test completed successfully
- All assertions passed

### ❌ Failed Test
```
test_customers.py::test_create_customer_success FAILED                  [ 10%]

AssertionError: assert 400 == 201
Expected 201, got 400: ...
```
- Red indicator
- Assertion failed
- Check error message for details
- Review test code and API response

### ⊘ Skipped Test
```
test_reports.py::test_refresh_token SKIPPED                             [ 5%]
```
- Yellow indicator
- Test deliberately skipped (may be unimplemented endpoint)
- Check test code for skip reason

### ⏭ Error During Setup
```
test_invoices.py ERRORS
Error during setup of test_create_invoice_success: fixture 'test_customer_and_product' raised InvalidFixtureRequest
```
- Test couldn't run due to fixture issue
- Check conftest.py and fixture dependencies
- Verify earlier tests passed

---

## Common Test Scenarios

### Scenario 1: Full Flow Test
Test complete business flow: Register → Login → Create Customer → Create Product → Create Invoice → Record Payment

```bash
# Run all tests in order
pytest tests/ -v --tb=short

# Watch output for progression
```

### Scenario 2: Isolated Module Testing
Test single module in isolation (e.g., just customers)

```bash
# Only customer tests
pytest tests/test_customers.py -v

# With verbose output
pytest tests/test_customers.py -vv

# Show print statements
pytest tests/test_customers.py -v -s
```

### Scenario 3: Error Handling Testing
Test API error scenarios (validation, permissions, not found)

```bash
# All negative tests
pytest -m negative -v

# Specific error test
pytest tests/test_customers.py::test_create_customer_duplicate_email -v
```

### Scenario 4: Performance/Load Testing
Run tests multiple times to check for stability

```bash
# Run 5 times
pytest tests/ -v --count=5

# Show slowest tests
pytest tests/ -v --durations=10
```

---

## Debugging Failed Tests

### Step 1: Identify the Failure
```bash
pytest tests/test_customers.py::test_create_customer_success -v
```

Output shows:
```
AssertionError: assert 400 == 201
Expected 201, got 400
```

### Step 2: Run with Verbose Output
```bash
pytest tests/test_customers.py::test_create_customer_success -vv -s
```

Adds print statements and detailed tracebacks.

### Step 3: Check Full Response
Modify test temporarily to print response:
```python
response = await authenticated_client.post("/customers", json=payload)
print(f"Status: {response.status_code}")
print(f"Response: {response.json()}")
```

OR use pytest's `-s` flag to see print statements:
```bash
pytest tests/test_customers.py::test_create_customer_success -v -s
```

### Step 4: Verify Backend is Running
```bash
# Check if backend is up
curl http://localhost:8000/api/v1/customers

# If 401, that's OK (means backend is responding)
# If Connection refused, backend is down
```

```bash
# Check Docker containers
docker compose ps

# Restart if needed
docker compose restart viyapar-backend
```

### Step 5: Check Test Data
Some tests might fail if test data already exists:

```bash
# Clear and restart database
docker compose down -v  # Remove volumes
docker compose up --build -d
```

---

## Test Reports

### HTML Report
Generate detailed HTML report with pass/fail breakdown:

```bash
pytest tests/ -v --html=report.html --self-contained-html
```

Open `report.html` in browser to view interactive report.

### Coverage Report
Generate code coverage report:

```bash
pytest tests/ --cov=app --cov-report=html --cov-report=term
```

Opens browser to view coverage details.

### Junit XML Report
Generate CI/CD compatible report:

```bash
pytest tests/ --junit-xml=test-results.xml
```

Use in GitLab CI, Jenkins, GitHub Actions, etc.

---

## Performance Benchmarking

### Measure Test Speed
```bash
# Show slowest tests
pytest tests/ -v --durations=10
```

Output:
```
test_invoices.py::test_create_invoice_success (3.21s)
test_reports.py::test_sales_report (2.15s)
test_customers.py::test_list_customers_success (1.87s)
```

### Stress Test
Run tests multiple times:

```bash
# Run 5 times
pytest tests/ -v --count=5

# Run continuous for 30 seconds
pytest tests/ -v --count=0 --maxfail=1
```

---

## Parallel Execution

### Run Tests in Parallel
Install pytest-xdist:
```bash
pip install pytest-xdist
```

Run with multiple workers:
```bash
pytest tests/ -v -n auto   # Use all CPU cores
pytest tests/ -v -n 4      # Use 4 workers
```

**Note**: May create multiple test users if running in parallel.

---

## CI/CD Integration

### GitHub Actions
```yaml
- name: Run API Tests
  run: |
    pip install -r tests/requirements.txt
    pytest tests/ -v --junit-xml=test-results.xml
```

### GitLab CI
```yaml
test:
  script:
    - pip install -r tests/requirements.txt
    - pytest tests/ -v --junit-xml=test-results.xml
```

### Jenkins
```groovy
stage('Test') {
    steps {
        sh 'pip install -r tests/requirements.txt'
        sh 'pytest tests/ -v --junit-xml=test-results.xml'
    }
}
```

---

## Troubleshooting

### Issue: "Connection refused"
**Cause**: Backend not running
```bash
# Start backend
docker compose up --build -d

# Verify it's running
docker compose logs viyapar-backend | tail -20
```

### Issue: "401 Unauthorized"
**Cause**: Authentication failed
```bash
# Check test setup is working
pytest tests/test_auth.py::test_register_user_success -v -s

# View setup logs
pytest tests/conftest.py -v
```

### Issue: "404 Customer not found"
**Cause**: Resource create failed or business isolation
```bash
# Run customer create test separately
pytest tests/test_customers.py::test_create_customer_success -v -s

# Check database
docker exec viyapar-db psql -U viyapar -d viyapar -c "SELECT COUNT(*) FROM customer;"
```

### Issue: "Timeout"
**Cause**: Backend too slow or hanging request
```bash
# Check backend logs
docker compose logs -f viyapar-backend

# Check database connection
docker compose logs -f viyapar-db

# Increase timeout in conftest.py
TIMEOUT = 60.0  # was 30.0
```

### Issue: "Duplicate Email"
**Cause**: Previous test data not cleaned up
```bash
# Clear database
docker compose down -v
docker compose up --build -d
```

---

## Advanced Usage

### Run Tests with Profiling
```bash
# Install line_profiler
pip install line-profiler

# Profile specific test
kernprof -l -v tests/test_auth.py::test_login_user_success
```

### Debug with PDB
```bash
# Drop into debugger on failure
pytest tests/test_customers.py -v --pdb

# Drop on exception
pytest tests/test_customers.py -v --pdbcls=IPython.terminal.debugger:Pdb
```

### Watch Tests While Developing
```bash
# Install pytest-watch
pip install pytest-watch

# Auto-run on file change
ptw tests/

# Run specific module on change
ptw tests/test_customers.py
```

---

## Best Practices

✅ **DO:**
- Run full suite before commit: `pytest tests/ -v`
- Use markers for organization: `pytest -m customers`
- Check coverage: `pytest --cov=app`
- Review HTML reports for failed tests
- Keep test database clean: `docker compose down -v`

❌ **DON'T:**
- Modify conftest.py unless required
- Run tests against production database
- Commit failing tests
- Ignore error messages
- Run tests in parallel without understanding implications

---

## Performance Targets

| Operation | Target Time |
|-----------|------------|
| Auth register | < 500ms |
| Auth login | < 300ms |
| Create customer | < 300ms |
| List customers (20 items) | < 200ms |
| Create invoice | < 500ms |
| Record payment | < 300ms |
| Generate report | < 1000ms |

---

## Support Information

**Test Suite Version**: 1.0.0  
**Last Updated**: March 14, 2026  
**API Version**: v1  
**Python Version**: 3.10+  
**Status**: ✅ Production Ready

For issues:
1. Check this guide first
2. Review test output carefully
3. Check backend logs: `docker compose logs viyapar-backend`
4. Verify test setup: `pytest tests/conftest.py -v`
5. Check database: `docker exec viyapar-db psql ... `
