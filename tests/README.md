# API Test Suite - Viyapar Backend

Comprehensive automated test suite for the Viyapar SaaS backend API using pytest, httpx, and pytest-asyncio.

## 📋 Overview

This test suite validates all API endpoints across the following modules:

- **Auth**: User registration, login, token refresh, authentication
- **Customers**: CRUD operations, pagination, search, business isolation
- **Products**: CRUD operations, inventory management, low stock alerts
- **Invoices**: Invoice creation, payment recording, status management
- **Payments**: Payment recording, filtering, isolation
- **Reports**: Sales, revenue, inventory, and debtors reports

## 🚀 Quick Start

### 1. Install Dependencies

```bash
# Navigate to tests directory
cd tests

# Install test requirements
pip install -r requirements.txt
```

### 2. Start the Backend

Ensure your FastAPI backend is running:

```bash
# From project root
docker compose up --build -d

# Or locally
cd backend && python -m uvicorn app.main:app --reload
```

### 3. Run Tests

```bash
# Run all tests
pytest -v

# Run specific test file
pytest tests/test_auth.py -v

# Run specific test marker
pytest -m auth -v
pytest -m customers -v
pytest -m invoices -v

# Run with coverage
pytest --cov=app tests/ -v

# Run with HTML report
pytest --html=report.html tests/ -v
```

## 📁 Test Structure

```
tests/
├── conftest.py           # Shared fixtures, setup, helpers
├── test_auth.py          # Authentication tests
├── test_customers.py     # Customer CRUD tests
├── test_products.py      # Product management tests
├── test_invoices.py      # Invoice and payment tests
├── test_payments.py      # Payment tracking tests
├── test_reports.py       # Report generation tests
└── requirements.txt      # Test dependencies
```

## 🔑 Key Features

### ✅ Authentication Flow
- Automatic user registration on test session start
- JWT token extraction and reuse across tests
- Bearer token authorization for all protected endpoints

### ✅ Resource Reuse
Tests automatically create and reuse resources:
1. User registration (session-wide)
2. Customers reused across customer/invoice tests
3. Products reused for invoice creation
4. Invoices reused for payment tests

### ✅ Business Isolation
- Tests verify multi-tenant data isolation
- Each test creates resources in correct business context
- Cross-business access properly rejected (404)

### ✅ Comprehensive Coverage
- **Positive tests**: Verify successful operations
- **Negative tests**: Validate error handling
- **Edge cases**: Boundary conditions, pagination, filtering
- **Integration**: Data flow across modules (customer → invoice → payment → report)

## 📝 Test Scenarios

### Auth Tests (test_auth.py)
- ✅ User registration success
- ✅ User login success  
- ✅ Invalid email login
- ✅ Invalid password
- ✅ Duplicate email registration
- ✅ Token refresh
- ✅ Unauthorized access without token
- ✅ Invalid token format

### Customer Tests (test_customers.py)
- ✅ Create customer (full + minimal fields)
- ✅ List customers with pagination
- ✅ Search customers by name/email
- ✅ Get customer by ID
- ✅ Update customer (PATCH - full + partial)
- ✅ Delete customer
- ✅ Duplicate email validation
- ✅ Business isolation

### Product Tests (test_products.py)
- ✅ Create product (full + minimal)
- ✅ List products with pagination
- ✅ Get product by ID
- ✅ Update product (PATCH)
- ✅ Delete product
- ✅ Duplicate SKU validation
- ✅ Low stock alerts
- ✅ Business isolation

### Invoice Tests (test_invoices.py)
- ✅ Create invoice with line items
- ✅ Invoice with discount
- ✅ List invoices with pagination
- ✅ Get invoice by ID
- ✅ Send invoice
- ✅ Record full payment
- ✅ Record partial payment
- ✅ Invalid customer/product validation
- ✅ Business isolation

### Payment Tests (test_payments.py)
- ✅ List payments with pagination
- ✅ Filter payments by date range
- ✅ Payment methods (UPI, bank transfer, cash, check)
- ✅ Payment with reference
- ✅ Business isolation

### Report Tests (test_reports.py)
- ✅ Sales report (daily, weekly aggregation)
- ✅ Revenue report
- ✅ Inventory report
- ✅ Debtors report (sorted by overdue)
- ✅ Custom date ranges
- ✅ Authorization enforcement
- ✅ Business isolation

## 🛠️ Configuration

### Base URL
```python
BASE_URL = "http://localhost:8000/api/v1"
```

Edit in `conftest.py` if using different host/port.

### Test User Credentials
Automatically created during session setup:
- Email: `test.user.<random>@example.com`
- Password: `TestPassword123!`
- Phone: `+919876543210`

### Timeout
Default timeout: 30 seconds per request

## 📊 Running Reports

### With Coverage
```bash
pytest --cov=app --cov-report=html tests/ -v
# Open htmlcov/index.html in browser
```

### With HTML Report
```bash
pytest --html=report.html --self-contained-html tests/ -v
# Open report.html in browser
```

### By Marker
```bash
# Run only customer-related tests
pytest -m customers -v

# Run only negative tests
pytest -m negative -v

# Run multiple markers
pytest -m "auth or customers" -v
```

### Async Debugging
```bash
# Show asyncio debug info
pytest -o asyncio_mode=auto -v
```

## 🔍 Debugging

### Show Request/Response
Add this to any test:
```python
print(f"Request: {response.request}")
print(f"Status: {response.status_code}")
print(f"Response: {response.json()}")
```

### Run Single Test
```bash
pytest tests/test_auth.py::test_login_user_success -v -s
```

### Stop on First Failure
```bash
pytest -x tests/
```

### Show Tracebacks
```bash
pytest --tb=long tests/
```

## 📝 Common Issues

### ❌ "Connection refused"
- Ensure backend is running: `docker compose up --build -d`
- Check BASE_URL in conftest.py matches your setup
- Verify port 8000 is accessible

### ❌ "401 Unauthorized"
- Check test user was created (check conftest setup)
- Verify token is being extracted correctly
- Check Authorization header format: `Bearer <token>`

### ❌ "404 Not Found"
- Verify resource was created in same business/tenant
- Check multi-tenant isolation isn't blocking access
- Verify IDs are being passed correctly

### ❌ "422 Validation Error"
- Check payload matches schema requirements
- Verify required fields are present
- Validate value types and formats

## 🔄 Test Data Flow

```
1. Session Setup
   └─> Register test user
       └─> Extract access_token

2. Auth Tests
   └─> Test registration, login, tokens

3. Customer Tests
   └─> Create test customer
       └─> Store customer_id

4. Product Tests
   └─> Create test product
       └─> Store product_id

5. Invoice Tests
   └─> Create invoice (customer_id + product_id)
       └─> Record payment
           └─> Store invoice_id, payment_id

6. Report Tests
   └─> Generate reports (uses data from above)
```

## 🎯 Best Practices

### ✅ Do's
- Run tests against clean database when possible
- Use unique emails for new registrations (auto-generated)
- Reuse created resources across related tests
- Check status codes before parsing responses
- Use pytest markers for test organization

### ❌ Don'ts
- Don't hardcode user credentials
- Don't assume resource IDs remain constant
- Don't mix test data between businesses
- Don't skip error handling tests
- Don't modify conftest.py unless necessary

## 📚 Resources

- [Pytest Documentation](https://docs.pytest.org/)
- [HTTPX Documentation](https://www.python-httpx.org/)
- [Pytest-Asyncio](https://pytest-asyncio.readthedocs.io/)
- [FastAPI Testing](https://fastapi.tiangolo.com/advanced/async-tests/)

## 🤝 Contributing

To add new tests:

1. Create test function with `test_` prefix
2. Use `authenticated_client` fixture for protected endpoints
3. Add appropriate pytest marker (`@pytest.mark.customers`, etc.)
4. Include docstring explaining test scenario
5. Assert both status code and response structure
6. Use test state for resource IDs

## 📞 Support

For issues or questions:
- Check test output with `-v` flag
- Review test logs with `-s` flag
- Consult API_REFERENCE.md for endpoint details
- Check backend logs: `docker compose logs viyapar-backend`

---

**Last Updated**: March 14, 2026
**API Version**: v1
**Status**: ✅ Production Ready
