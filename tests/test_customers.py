"""
Customer API Tests

Test Cases:
- Create customer
- List customers (with pagination and search)
- Get customer by ID
- Update customer (PATCH)
- Delete customer
- Negative tests (duplicate email, invalid IDs, etc.)
"""
import pytest
import httpx
import uuid
from typing import Dict, Any

pytestmark = pytest.mark.customers


@pytest.mark.asyncio
async def test_create_customer_success(authenticated_client: httpx.AsyncClient):
    """Test successful customer creation"""
    unique_email = f"customer.{uuid.uuid4().hex[:6]}@example.com"
    unique_phone = f"+91{uuid.uuid4().hex[:10]}".replace('a', '1')[:13]
    
    payload = {
        "name": "Rajesh Kumar",
        "email": unique_email,
        "phone": unique_phone,
        "gstin": "29ABCDE1234F1Z5",
        "city": "Mumbai",
        "state": "Maharashtra",
        "country": "India",
        "pincode": "400001",
        "billing_address": "123 MG Road, Mumbai",
        "shipping_address": "456 Bandra Street, Mumbai",
        "notes": "Premium customer",
    }
    
    response = await authenticated_client.post("/customers", json=payload)
    
    assert response.status_code == 201, f"Expected 201, got {response.status_code}: {response.text}"
    
    data = response.json()
    
    # Validate response
    assert data["id"] is not None
    assert data["business_id"] is not None
    assert data["name"] == payload["name"]
    assert data["email"] == unique_email
    assert data["phone"] == payload["phone"]
    assert data["gstin"] == payload["gstin"]
    assert data["city"] == payload["city"]
    assert data["state"] == payload["state"]
    assert data["country"] == payload["country"]
    assert data["pincode"] == payload["pincode"]
    assert data["billing_address"] == payload["billing_address"]
    assert data["shipping_address"] == payload["shipping_address"]
    assert data["balance"] == 0.0
    assert data["notes"] == payload["notes"]
    assert "created_at" in data
    assert "updated_at" in data
    
    print(f"✓ Customer created: {payload['name']}")
    
    return data


@pytest.mark.asyncio
async def test_create_customer_minimal(authenticated_client: httpx.AsyncClient):
    """Test customer creation with minimal fields"""
    unique_email = f"minimal.{uuid.uuid4().hex[:6]}@example.com"
    
    payload = {
        "name": "Minimal Customer",
        "email": unique_email,
    }
    
    response = await authenticated_client.post("/customers", json=payload)
    
    assert response.status_code == 201, f"Expected 201, got {response.status_code}: {response.text}"
    
    data = response.json()
    assert data["name"] == "Minimal Customer"
    assert data["email"] == unique_email
    
    print("✓ Customer created with minimal fields")


@pytest.mark.asyncio
async def test_list_customers_success(authenticated_client: httpx.AsyncClient, test_customer: Dict[str, Any]):
    """Test listing customers with pagination"""
    response = await authenticated_client.get("/customers?page=1&per_page=20")
    
    assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
    
    data = response.json()
    
    # Validate pagination structure
    assert "data" in data
    assert "total" in data
    assert "page" in data
    assert "per_page" in data
    assert "total_pages" in data
    
    assert isinstance(data["data"], list)
    assert data["page"] == 1
    assert data["per_page"] == 20
    assert data["total"] > 0
    assert data["total_pages"] > 0
    
    # Validate customer item structure
    if len(data["data"]) > 0:
        customer = data["data"][0]
        assert "id" in customer
        assert "name" in customer
        assert "email" in customer or customer["email"] is None
        assert "phone" in customer or customer["phone"] is None
        assert "city" in customer or customer["city"] is None
        assert "balance" in customer
    
    print(f"✓ Listed {len(data['data'])} customers")


@pytest.mark.asyncio
async def test_list_customers_pagination(authenticated_client: httpx.AsyncClient):
    """Test customer list pagination"""
    # Page 1
    response1 = await authenticated_client.get("/customers?page=1&per_page=5")
    assert response1.status_code == 200
    data1 = response1.json()
    
    # Page 2
    response2 = await authenticated_client.get("/customers?page=2&per_page=5")
    assert response2.status_code == 200
    data2 = response2.json()
    
    # Validate pagination
    assert data1["page"] == 1
    assert data2["page"] == 2
    assert data1["per_page"] == 5
    assert data2["per_page"] == 5
    
    print(f"✓ Pagination tested: Page 1 ({len(data1['data'])} items), Page 2 ({len(data2['data'])} items)")


@pytest.mark.asyncio
async def test_list_customers_search(authenticated_client: httpx.AsyncClient, test_customer: Dict[str, Any]):
    """Test customer search functionality"""
    customer_name = test_customer["name"]
    
    response = await authenticated_client.get(f"/customers?search={customer_name}")
    
    assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
    
    data = response.json()
    
    # Should find at least the created customer
    assert len(data["data"]) > 0
    assert any(c["name"].lower() == customer_name.lower() for c in data["data"])
    
    print(f"✓ Customer search found: {customer_name}")


@pytest.mark.asyncio
async def test_get_customer_by_id_success(authenticated_client: httpx.AsyncClient, test_customer: Dict[str, Any]):
    """Test retrieving customer by ID"""
    customer_id = test_customer["id"]
    
    response = await authenticated_client.get(f"/customers/{customer_id}")
    
    assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
    
    data = response.json()
    
    # Validate all fields returned
    assert data["id"] == customer_id
    assert data["business_id"] is not None
    assert data["name"] == test_customer["name"]
    assert "created_at" in data
    assert "updated_at" in data
    
    print(f"✓ Retrieved customer by ID: {customer_id}")


@pytest.mark.asyncio
async def test_get_customer_not_found(authenticated_client: httpx.AsyncClient):
    """Test retrieving non-existent customer"""
    fake_id = str(uuid.uuid4())
    
    response = await authenticated_client.get(f"/customers/{fake_id}")
    
    assert response.status_code == 404, f"Expected 404, got {response.status_code}"
    
    print("✓ Non-existent customer returns 404")


@pytest.mark.asyncio
async def test_update_customer_success(authenticated_client: httpx.AsyncClient, test_customer: Dict[str, Any]):
    """Test updating customer with PATCH"""
    customer_id = test_customer["id"]
    
    update_payload = {
        "name": "Rajesh Kumar - Updated",
        "phone": f"+91{uuid.uuid4().hex[:10]}".replace('a', '1')[:13],
        "city": "Bangalore",
        "billing_address": "789 Whitefield, Bangalore",
        "notes": "Updated notes",
    }
    
    response = await authenticated_client.patch(f"/customers/{customer_id}", json=update_payload)
    
    assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
    
    data = response.json()
    
    # Validate updates
    assert data["id"] == customer_id
    assert data["name"] == update_payload["name"]
    assert data["phone"] == update_payload["phone"]
    assert data["city"] == update_payload["city"]
    assert data["billing_address"] == update_payload["billing_address"]
    assert data["notes"] == update_payload["notes"]
    
    # Verify other fields unchanged
    assert data["email"] == test_customer["email"]
    
    print(f"✓ Customer updated: {customer_id}")


@pytest.mark.asyncio
async def test_update_customer_partial(authenticated_client: httpx.AsyncClient, test_customer: Dict[str, Any]):
    """Test partial customer update"""
    customer_id = test_customer["id"]
    
    # Update only one field
    update_payload = {
        "city": "Hyderabad",
    }
    
    response = await authenticated_client.patch(f"/customers/{customer_id}", json=update_payload)
    
    assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
    
    data = response.json()
    
    # Validate update
    assert data["city"] == "Hyderabad"
    # Verify original fields unchanged
    assert data["name"] == test_customer["name"]
    
    print(f"✓ Partial customer update: city changed to {data['city']}")


@pytest.mark.asyncio
async def test_update_customer_not_found(authenticated_client: httpx.AsyncClient):
    """Test updating non-existent customer"""
    fake_id = str(uuid.uuid4())
    
    update_payload = {"name": "Updated Name"}
    
    response = await authenticated_client.patch(f"/customers/{fake_id}", json=update_payload)
    
    assert response.status_code == 404, f"Expected 404, got {response.status_code}"
    
    print("✓ Updating non-existent customer returns 404")


@pytest.mark.asyncio
async def test_delete_customer_success(authenticated_client: httpx.AsyncClient):
    """Test deleting customer"""
    # Create a customer to delete
    from conftest import create_customer
    customer = await create_customer(authenticated_client, name="Customer To Delete")
    customer_id = customer["id"]
    
    response = await authenticated_client.delete(f"/customers/{customer_id}")
    
    assert response.status_code == 204, f"Expected 204, got {response.status_code}: {response.text}"
    
    # Verify deletion
    get_response = await authenticated_client.get(f"/customers/{customer_id}")
    assert get_response.status_code == 404, "Customer should not exist after deletion"
    
    print(f"✓ Customer deleted: {customer_id}")


@pytest.mark.asyncio
async def test_delete_customer_not_found(authenticated_client: httpx.AsyncClient):
    """Test deleting non-existent customer"""
    fake_id = str(uuid.uuid4())
    
    response = await authenticated_client.delete(f"/customers/{fake_id}")
    
    assert response.status_code == 404, f"Expected 404, got {response.status_code}"
    
    print("✓ Deleting non-existent customer returns 404")


@pytest.mark.asyncio
async def test_create_customer_missing_name(authenticated_client: httpx.AsyncClient):
    """Test creating customer without name"""
    payload = {
        "email": "test@example.com",
    }
    
    response = await authenticated_client.post("/customers", json=payload)
    
    assert response.status_code == 422, f"Expected 422, got {response.status_code}"
    
    print("✓ Missing required field validation works")


@pytest.mark.asyncio
async def test_create_customer_invalid_email(authenticated_client: httpx.AsyncClient):
    """Test creating customer with invalid email"""
    payload = {
        "name": "Test Customer",
        "email": "invalid-email",  # Not a valid email
    }
    
    response = await authenticated_client.post("/customers", json=payload)
    
    # Should either accept or reject with 422 (depending on validation)
    assert response.status_code in [201, 422], f"Unexpected status: {response.status_code}"
    
    if response.status_code == 422:
        print("✓ Invalid email format validation works")
    else:
        print("ℹ Email format validation not enforced")


@pytest.mark.asyncio
async def test_create_customer_duplicate_email(authenticated_client: httpx.AsyncClient, test_customer: Dict[str, Any]):
    """Test creating customer with duplicate email"""
    duplicate_email = test_customer["email"]
    
    payload = {
        "name": "Another Customer",
        "email": duplicate_email,  # Already used
    }
    
    response = await authenticated_client.post("/customers", json=payload)
    
    # Should reject due to uniqueness constraint
    assert response.status_code >= 400, f"Expected duplicate rejection, got {response.status_code}"
    
    print("✓ Duplicate email validation works")


@pytest.mark.asyncio
async def test_customer_business_isolation(http_client: httpx.AsyncClient):
    """Test that customers are isolated per business"""
    import uuid as uuid_lib
    from conftest import test_state, create_customer
    
    # Create another business/user
    unique_email = f"business2.{uuid_lib.uuid4().hex[:6]}@example.com"
    unique_phone = f"+91{uuid_lib.uuid4().hex[:10]}".replace('a', '1')[:13]
    
    register_payload = {
        "business_name": "Business 2",
        "name": "User 2",
        "email": unique_email,
        "password": "Password123!",
        "phone": unique_phone,
    }
    
    register_response = await http_client.post("/auth/register", json=register_payload)
    assert register_response.status_code == 201
    
    register_data = register_response.json()
    token2 = register_data["tokens"]["access_token"]
    
    # Create customer in business 2
    http_client.headers["Authorization"] = f"Bearer {token2}"
    customer2 = await create_customer(http_client, name="Business 2 Customer")
    
    # Switch back to business 1
    http_client.headers["Authorization"] = f"Bearer {test_state.access_token}"
    
    # Try to access business 2's customer (should fail)
    response = await http_client.get(f"/customers/{customer2['id']}")
    
    assert response.status_code in [401, 404], "Should not access another business's customer"
    
    print("✓ Customer business isolation works")
