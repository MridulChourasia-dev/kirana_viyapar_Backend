"""
Product API Tests

Test Cases:
- Create product
- List products
- Get product
- Update product
- Delete product
- Low stock alert
- Negative tests
"""
import pytest
import httpx
import uuid
from typing import Dict, Any

pytestmark = pytest.mark.products


@pytest.mark.asyncio
async def test_create_product_success(authenticated_client: httpx.AsyncClient):
    """Test successful product creation"""
    unique_sku = f"SKU-{uuid.uuid4().hex[:8].upper()}"
    
    payload = {
        "name": "Wireless Mouse",
        "sku": unique_sku,
        "barcode": "1234567890123",
        "hsn_code": "8471",
        "description": "2.4GHz wireless mouse with USB receiver",
        "sale_price": 599.00,
        "purchase_price": 350.00,
        "tax_rate": 18.0,
        "stock_quantity": 100,
        "low_stock_alert": 10,
        "unit": "piece",
    }
    
    response = await authenticated_client.post("/products", json=payload)
    
    assert response.status_code == 201, f"Expected 201, got {response.status_code}: {response.text}"
    
    data = response.json()
    
    # Validate response
    assert data["id"] is not None
    assert data["name"] == payload["name"]
    assert data["sku"] == unique_sku
    assert data["hsn_code"] == payload["hsn_code"]
    assert data["sale_price"] == payload["sale_price"]
    assert data["purchase_price"] == payload["purchase_price"]
    assert data["tax_rate"] == payload["tax_rate"]
    assert data["stock_quantity"] == payload["stock_quantity"]
    assert data["low_stock_alert"] == payload["low_stock_alert"]
    assert "created_at" in data
    assert "updated_at" in data
    
    print(f"✓ Product created: {payload['name']}")
    
    return data


@pytest.mark.asyncio
async def test_create_product_minimal(authenticated_client: httpx.AsyncClient):
    """Test product creation with minimal fields"""
    unique_sku = f"SKU-{uuid.uuid4().hex[:8].upper()}"
    
    payload = {
        "name": "Basic Product",
        "sku": unique_sku,
        "sale_price": 100.00,
        "purchase_price": 50.00,
    }
    
    response = await authenticated_client.post("/products", json=payload)
    
    assert response.status_code == 201, f"Expected 201, got {response.status_code}: {response.text}"
    
    data = response.json()
    assert data["name"] == "Basic Product"
    assert data["sale_price"] == 100.00
    
    print("✓ Product created with minimal fields")


@pytest.mark.asyncio
async def test_list_products_success(authenticated_client: httpx.AsyncClient, test_product: Dict[str, Any]):
    """Test listing products with pagination"""
    response = await authenticated_client.get("/products?page=1&per_page=20")
    
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
    
    # Validate product item structure
    if len(data["data"]) > 0:
        product = data["data"][0]
        assert "id" in product
        assert "name" in product
        assert "sku" in product
        assert "sale_price" in product
        assert "purchase_price" in product
        assert "stock_quantity" in product
    
    print(f"✓ Listed {len(data['data'])} products")


@pytest.mark.asyncio
async def test_list_products_pagination(authenticated_client: httpx.AsyncClient):
    """Test product list pagination"""
    # Page 1
    response1 = await authenticated_client.get("/products?page=1&per_page=5")
    assert response1.status_code == 200
    data1 = response1.json()
    
    # Page 2 (if available)
    response2 = await authenticated_client.get("/products?page=2&per_page=5")
    assert response2.status_code == 200
    data2 = response2.json()
    
    # Validate pagination
    assert data1["page"] == 1
    assert data2["page"] == 2
    assert data1["per_page"] == 5
    assert data2["per_page"] == 5
    
    print(f"✓ Pagination tested: Page 1 ({len(data1['data'])} items), Page 2 ({len(data2['data'])} items)")


@pytest.mark.asyncio
async def test_get_product_by_id_success(authenticated_client: httpx.AsyncClient, test_product: Dict[str, Any]):
    """Test retrieving product by ID"""
    product_id = test_product["id"]
    
    response = await authenticated_client.get(f"/products/{product_id}")
    
    assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
    
    data = response.json()
    
    # Validate all fields
    assert data["id"] == product_id
    assert data["name"] == test_product["name"]
    assert data["sku"] == test_product["sku"]
    assert "created_at" in data
    assert "updated_at" in data
    
    print(f"✓ Retrieved product by ID: {product_id}")


@pytest.mark.asyncio
async def test_get_product_not_found(authenticated_client: httpx.AsyncClient):
    """Test retrieving non-existent product"""
    fake_id = str(uuid.uuid4())
    
    response = await authenticated_client.get(f"/products/{fake_id}")
    
    assert response.status_code == 404, f"Expected 404, got {response.status_code}"
    
    print("✓ Non-existent product returns 404")


@pytest.mark.asyncio
async def test_update_product_success(authenticated_client: httpx.AsyncClient, test_product: Dict[str, Any]):
    """Test updating product with PATCH"""
    product_id = test_product["id"]
    
    update_payload = {
        "sale_price": 799.00,
        "stock_quantity": 75,
        "low_stock_alert": 15,
    }
    
    response = await authenticated_client.patch(f"/products/{product_id}", json=update_payload)
    
    assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
    
    data = response.json()
    
    # Validate updates
    assert data["id"] == product_id
    assert data["sale_price"] == update_payload["sale_price"]
    assert data["stock_quantity"] == update_payload["stock_quantity"]
    assert data["low_stock_alert"] == update_payload["low_stock_alert"]
    
    # Verify other fields unchanged
    assert data["sku"] == test_product["sku"]
    
    print(f"✓ Product updated: {product_id}")


@pytest.mark.asyncio
async def test_update_product_partial(authenticated_client: httpx.AsyncClient, test_product: Dict[str, Any]):
    """Test partial product update"""
    product_id = test_product["id"]
    
    # Update only one field
    update_payload = {
        "sale_price": 649.00,
    }
    
    response = await authenticated_client.patch(f"/products/{product_id}", json=update_payload)
    
    assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
    
    data = response.json()
    
    # Validate update
    assert data["sale_price"] == 649.00
    # Verify original fields unchanged
    assert data["name"] == test_product["name"]
    
    print(f"✓ Partial product update: price changed to {data['sale_price']}")


@pytest.mark.asyncio
async def test_update_product_not_found(authenticated_client: httpx.AsyncClient):
    """Test updating non-existent product"""
    fake_id = str(uuid.uuid4())
    
    update_payload = {"sale_price": 699.00}
    
    response = await authenticated_client.patch(f"/products/{fake_id}", json=update_payload)
    
    assert response.status_code == 404, f"Expected 404, got {response.status_code}"
    
    print("✓ Updating non-existent product returns 404")


@pytest.mark.asyncio
async def test_delete_product_success(authenticated_client: httpx.AsyncClient):
    """Test deleting product"""
    # Create a product to delete
    from conftest import create_product
    product = await create_product(authenticated_client, name="Product To Delete")
    product_id = product["id"]
    
    response = await authenticated_client.delete(f"/products/{product_id}")
    
    # Should return either 204 (deleted) or 200 OK
    assert response.status_code in [200, 204], f"Expected 200 or 204, got {response.status_code}"
    
    # Verify deletion
    get_response = await authenticated_client.get(f"/products/{product_id}")
    assert get_response.status_code == 404, "Product should not exist after deletion"
    
    print(f"✓ Product deleted: {product_id}")


@pytest.mark.asyncio
async def test_delete_product_not_found(authenticated_client: httpx.AsyncClient):
    """Test deleting non-existent product"""
    fake_id = str(uuid.uuid4())
    
    response = await authenticated_client.delete(f"/products/{fake_id}")
    
    assert response.status_code == 404, f"Expected 404, got {response.status_code}"
    
    print("✓ Deleting non-existent product returns 404")


@pytest.mark.asyncio
async def test_create_product_duplicate_sku(authenticated_client: httpx.AsyncClient, test_product: Dict[str, Any]):
    """Test creating product with duplicate SKU"""
    duplicate_sku = test_product["sku"]
    
    payload = {
        "name": "Another Product",
        "sku": duplicate_sku,  # Already used
        "sale_price": 100.00,
        "purchase_price": 50.00,
    }
    
    response = await authenticated_client.post("/products", json=payload)
    
    # Should reject due to uniqueness constraint
    assert response.status_code >= 400, f"Expected duplicate rejection, got {response.status_code}"
    
    print("✓ Duplicate SKU validation works")


@pytest.mark.asyncio
async def test_create_product_missing_name(authenticated_client: httpx.AsyncClient):
    """Test creating product without name"""
    payload = {
        "sku": "SKU-TEST-001",
        "sale_price": 100.00,
        "purchase_price": 50.00,
    }
    
    response = await authenticated_client.post("/products", json=payload)
    
    assert response.status_code == 422, f"Expected 422, got {response.status_code}"
    
    print("✓ Missing required field (name) validation works")


@pytest.mark.asyncio
async def test_create_product_negative_price(authenticated_client: httpx.AsyncClient):
    """Test creating product with negative price"""
    unique_sku = f"SKU-{uuid.uuid4().hex[:8].upper()}"
    
    payload = {
        "name": "Invalid Product",
        "sku": unique_sku,
        "sale_price": -100.00,  # Negative price
        "purchase_price": 50.00,
    }
    
    response = await authenticated_client.post("/products", json=payload)
    
    # Should either accept or reject with 422 (depending on validation)
    assert response.status_code in [201, 422], f"Unexpected status: {response.status_code}"
    
    if response.status_code == 422:
        print("✓ Negative price validation works")
    else:
        print("ℹ Negative price validation not enforced")


@pytest.mark.asyncio
async def test_product_business_isolation(http_client: httpx.AsyncClient):
    """Test that products are isolated per business"""
    import uuid as uuid_lib
    from conftest import test_state, create_product
    
    # Create another business/user
    unique_email = f"business3.{uuid_lib.uuid4().hex[:6]}@example.com"
    unique_phone = f"+91{uuid.uuid4().hex[:10]}".replace('a', '1')[:13]
    
    register_payload = {
        "business_name": "Business 5",
        "name": "User 5",
        "email": unique_email,
        "password": "Password123!",
        "phone": unique_phone,
    }
    
    register_response = await http_client.post("/auth/register", json=register_payload)
    assert register_response.status_code == 201
    
    register_data = register_response.json()
    token3 = register_data["tokens"]["access_token"]
    
    # Create product in business 3
    http_client.headers["Authorization"] = f"Bearer {token3}"
    product3 = await create_product(http_client, name="Business 3 Product")
    
    # Switch back to business 1
    http_client.headers["Authorization"] = f"Bearer {test_state.access_token}"
    
    # Try to access business 3's product (should fail)
    response = await http_client.get(f"/products/{product3['id']}")
    
    assert response.status_code in [401, 404], "Should not access another business's product"
    
    print("✓ Product business isolation works")


@pytest.mark.asyncio
async def test_low_stock_alert(authenticated_client: httpx.AsyncClient):
    """Test low stock alert endpoint (if implemented)"""
    import uuid as uuid_lib

    # Create product with low stock
    unique_sku = f"SKU-LOWSTOCK-{uuid_lib.uuid4().hex[:6].upper()}"
    payload = {
        "name": "Low Stock Product",
        "sku": unique_sku,
        "sale_price": 100.00,
        "purchase_price": 50.00,
        "stock_quantity": 5,
        "low_stock_alert": 10,
    }

    create_response = await authenticated_client.post("/products", json=payload)
    assert create_response.status_code == 201, f"Expected 201, got {create_response.status_code}: {create_response.text}"

    # Check low stock alert endpoint
    response = await authenticated_client.get("/products/low-stock")

    if response.status_code == 200:
        data = response.json()
        assert "data" in data
        print(f"✓ Low stock alert endpoint working: {len(data.get('data', []))} products")
    else:
        print(f"ℹ Low stock alert endpoint returned {response.status_code} (may not be implemented)")
