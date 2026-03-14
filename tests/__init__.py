"""
API Test Suite for Viyapar Backend

Comprehensive integration tests for all API endpoints including:
- Authentication (Registration, Login, Token Refresh)
- Customers (CRUD, Search, Pagination)
- Products (CRUD, Stock Management)
- Invoices (Creation, Payments, Status)
- Payments (Recording, Filtering)
- Reports (Sales, Revenue, Inventory, Debtors)

Run tests with:
    pytest -v
    pytest -m auth -v
    pytest tests/test_customers.py -v
"""

__version__ = "1.0.0"
__author__ = "Viyapar QA Team"
