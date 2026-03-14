"""
Pytest configuration and shared fixtures for API tests
"""
import pytest
import httpx
import uuid
from datetime import datetime
from typing import AsyncGenerator, Dict, Any

# ─────────────────────────────────────────
# Configuration
# ─────────────────────────────────────────

BASE_URL = "http://localhost:8000/api/v1"
TIMEOUT = 30.0

# Test data
TEST_BUSINESS_NAME = f"Test Business {datetime.now().strftime('%Y%m%d%H%M%S')}"
TEST_USER_EMAIL = f"test.user.{uuid.uuid4().hex[:8]}@example.com"
TEST_USER_PASSWORD = "TestPassword123!"
TEST_USER_PHONE = f"+91{uuid.uuid4().hex[:10].replace('0', '1')[:10]}"  # Generate unique phone


# ─────────────────────────────────────────
# Global State for Resource Sharing
# ─────────────────────────────────────────

class TestState:
    """Stores test data and created resource IDs for reuse across tests"""
    
    def __init__(self):
        self.user_id = None
        self.business_id = None
        self.access_token = None
        self.refresh_token = None
        self.customer_ids = []
        self.product_ids = []
        self.category_id = None
        self.invoice_ids = []
        self.payment_ids = []


# Global state instance
test_state = TestState()


# ─────────────────────────────────────────
# Fixtures
# ─────────────────────────────────────────

@pytest.fixture
async def http_client() -> AsyncGenerator[httpx.AsyncClient, None]:
    """Async HTTP client for API requests"""
    async with httpx.AsyncClient(base_url=BASE_URL, timeout=TIMEOUT, follow_redirects=True) as client:
        yield client


@pytest.fixture
async def authenticated_client(http_client: httpx.AsyncClient) -> AsyncGenerator[httpx.AsyncClient, None]:
    """HTTP client with authentication header"""
    if not test_state.access_token:
        raise RuntimeError("No access token available. Register and login first.")
    
    # Add authorization header
    http_client.headers["Authorization"] = f"Bearer {test_state.access_token}"
    yield http_client
    
    # Clean up headers
    if "Authorization" in http_client.headers:
        del http_client.headers["Authorization"]


@pytest.fixture(scope="session", autouse=True)
async def setup_test_user():
    """Setup test user and store tokens for all tests"""
    async with httpx.AsyncClient(base_url=BASE_URL, timeout=TIMEOUT) as client:
        # Register user
        register_payload = {
            "business_name": TEST_BUSINESS_NAME,
            "name": "Test User",
            "email": TEST_USER_EMAIL,
            "password": TEST_USER_PASSWORD,
            "phone": TEST_USER_PHONE,
        }
        
        register_response = await client.post("/auth/register", json=register_payload)
        assert register_response.status_code == 201, f"Registration failed: {register_response.text}"
        
        register_data = register_response.json()
        test_state.user_id = register_data["user"]["id"]
        test_state.business_id = register_data["business"]["id"]
        test_state.access_token = register_data["tokens"]["access_token"]
        test_state.refresh_token = register_data["tokens"].get("refresh_token")
        
        print(f"\n✓ Test user registered: {TEST_USER_EMAIL}")
        print(f"  User ID: {test_state.user_id}")
        print(f"  Business ID: {test_state.business_id}")


# ─────────────────────────────────────────
# Helper Functions for Test Data Creation
# ─────────────────────────────────────────

def generate_unique_phone() -> str:
    """Generate a unique phone number"""
    random_suffix = uuid.uuid4().hex[:10].replace('a', '1').replace('b', '2')[:10]
    return f"+91{random_suffix}"


async def create_customer(
    client: httpx.AsyncClient,
    name: str = "Test Customer",
    email: str = None,
    phone: str = None,
    gstin: str = "29ABCDE1234F1Z5",
    city: str = "Mumbai",
    state: str = "Maharashtra",
    country: str = "India",
    pincode: str = "400001",
    billing_address: str = "123 MG Road",
    shipping_address: str = "456 Bandra Street",
    notes: str = "Test customer",
) -> Dict[str, Any]:
    """Helper to create a test customer"""
    if not email:
        email = f"customer.{uuid.uuid4().hex[:6]}@example.com"
    if not phone:
        phone = generate_unique_phone()
    
    payload = {
        "name": name,
        "email": email,
        "phone": phone,
        "gstin": gstin,
        "city": city,
        "state": state,
        "country": country,
        "pincode": pincode,
        "billing_address": billing_address,
        "shipping_address": shipping_address,
        "notes": notes,
    }
    
    response = await client.post("/customers", json=payload)
    assert response.status_code == 201, f"Create customer failed: {response.text}"
    
    customer_data = response.json()
    test_state.customer_ids.append(customer_data["id"])
    return customer_data


async def create_product(
    client: httpx.AsyncClient,
    name: str = "Test Product",
    sku: str = None,
    sale_price: float = 599.00,
    purchase_price: float = 350.00,
    stock_quantity: int = 100,
    tax_rate: float = 18.0,
    hsn_code: str = "8471",
    unit: str = "piece",
) -> Dict[str, Any]:
    """Helper to create a test product"""
    if not sku:
        sku = f"SKU-{uuid.uuid4().hex[:8].upper()}"
    
    payload = {
        "name": name,
        "sku": sku,
        "sale_price": sale_price,
        "purchase_price": purchase_price,
        "stock_quantity": stock_quantity,
        "tax_rate": tax_rate,
        "hsn_code": hsn_code,
        "unit": unit,
        "description": f"Test product - {name}",
    }
    
    response = await client.post("/products", json=payload)
    assert response.status_code == 201, f"Create product failed: {response.text}"
    
    product_data = response.json()
    test_state.product_ids.append(product_data["id"])
    return product_data


async def create_invoice(
    client: httpx.AsyncClient,
    customer_id: str,
    items: list,
    customer_name: str = "Test Customer",
    due_date: str = "2026-04-13",
    payment_mode: str = "upi",
    notes: str = "Test invoice",
) -> Dict[str, Any]:
    """Helper to create a test invoice"""
    from datetime import datetime, timedelta
    
    invoice_date = datetime.now().strftime("%Y-%m-%d")
    if not due_date:
        due_date = (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d")
    
    normalized_items = []
    for item in items:
        normalized = dict(item)
        normalized.setdefault("product_name", "Test Product")
        normalized_items.append(normalized)

    payload = {
        "customer_id": customer_id,
        "customer_name": customer_name,
        "invoice_date": invoice_date,
        "due_date": due_date,
        "items": normalized_items,
        "payment_mode": payment_mode,
        "notes": notes,
    }
    
    response = await client.post("/invoices", json=payload)
    assert response.status_code == 201, f"Create invoice failed: {response.text}"
    
    invoice_data = response.json()
    test_state.invoice_ids.append(invoice_data["id"])
    return invoice_data


async def login_user(
    client: httpx.AsyncClient,
    email: str = TEST_USER_EMAIL,
    password: str = TEST_USER_PASSWORD,
) -> Dict[str, Any]:
    """Helper to login and optionally refresh shared auth state."""
    payload = {
        "email": email,
        "password": password,
    }

    response = await client.post("/auth/login", json=payload)
    assert response.status_code == 200, f"Login failed: {response.text}"

    data = response.json()
    tokens = data.get("tokens", {})
    access_token = tokens.get("access_token")
    refresh_token = tokens.get("refresh_token")

    if email == TEST_USER_EMAIL and access_token:
        test_state.access_token = access_token
    if email == TEST_USER_EMAIL and refresh_token:
        test_state.refresh_token = refresh_token

    return data


# ─────────────────────────────────────────
# Fixture for Shared Resources
# ─────────────────────────────────────────

@pytest.fixture
async def test_customer(authenticated_client: httpx.AsyncClient) -> Dict[str, Any]:
    """Create a test customer for use in tests"""
    return await create_customer(authenticated_client)


@pytest.fixture
async def test_product(authenticated_client: httpx.AsyncClient) -> Dict[str, Any]:
    """Create a test product for use in tests"""
    return await create_product(authenticated_client)


@pytest.fixture
async def test_customer_and_product(
    authenticated_client: httpx.AsyncClient,
) -> tuple[Dict[str, Any], Dict[str, Any]]:
    """Create both customer and product for invoice testing"""
    customer = await create_customer(authenticated_client)
    product = await create_product(authenticated_client)
    return customer, product


# ─────────────────────────────────────────
# Markers for Test Organization
# ─────────────────────────────────────────

def pytest_configure(config):
    """Register custom pytest markers"""
    config.addinivalue_line("markers", "auth: Auth API tests")
    config.addinivalue_line("markers", "customers: Customer API tests")
    config.addinivalue_line("markers", "products: Product API tests")
    config.addinivalue_line("markers", "invoices: Invoice API tests")
    config.addinivalue_line("markers", "payments: Payment API tests")
    config.addinivalue_line("markers", "reports: Report API tests")
    config.addinivalue_line("markers", "negative: Negative/error tests")
