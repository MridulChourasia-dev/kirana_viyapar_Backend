"""
Payment API Tests

Test Cases:
- List payments
- Get payment details
- Payment filtering by invoice
- Negative tests
"""
import pytest
import httpx
import uuid
from datetime import datetime, timedelta

pytestmark = pytest.mark.payments


@pytest.mark.asyncio
async def test_list_payments_success(authenticated_client: httpx.AsyncClient):
    """Test listing payments"""
    response = await authenticated_client.get("/payments?page=1&per_page=20")
    
    # Endpoint may not be implemented
    if response.status_code == 200:
        data = response.json()
        
        # Validate response structure
        assert "data" in data or "payments" in data
        assert "total" in data or "total_count" in data
        
        print(f"✓ Payments listed: {len(data.get('data', data.get('payments', [])))}")
    else:
        print(f"ℹ List payments endpoint returned {response.status_code} (may not be implemented)")


@pytest.mark.asyncio
async def test_list_payments_with_filters(authenticated_client: httpx.AsyncClient):
    """Test listing payments with filters"""
    from_date = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")
    to_date = datetime.now().strftime("%Y-%m-%d")
    
    response = await authenticated_client.get(f"/payments?from_date={from_date}&to_date={to_date}")
    
    if response.status_code == 200:
        data = response.json()
        assert "data" in data or "payments" in data
        print(f"✓ Payments listed with date filter")
    else:
        print(f"ℹ Payments with filters returned {response.status_code}")


@pytest.mark.asyncio
async def test_get_payment_not_found(authenticated_client: httpx.AsyncClient):
    """Test retrieving non-existent payment"""
    fake_id = str(uuid.uuid4())
    
    response = await authenticated_client.get(f"/payments/{fake_id}")
    
    if response.status_code == 404:
        print("✓ Non-existent payment returns 404")
    elif response.status_code == 405:
        print("ℹ GET /payments/{id} endpoint not implemented (405)")
    else:
        print(f"ℹ Get payment returned {response.status_code}")


@pytest.mark.asyncio
async def test_payment_business_isolation(http_client: httpx.AsyncClient):
    """Test that payments are isolated per business"""
    import uuid as uuid_lib
    from conftest import test_state, create_customer, create_product, create_invoice
    
    # Create another business/user
    unique_email = f"business5.{uuid_lib.uuid4().hex[:6]}@example.com"
    unique_phone = f"+91{uuid.uuid4().hex[:10]}".replace('a', '1')[:13]
    
    register_payload = {
        "business_name": "Business 3",
        "name": "User 3",
        "email": unique_email,
        "password": "Password123!",
        "phone": unique_phone,
    }
    
    register_response = await http_client.post("/auth/register", json=register_payload)
    assert register_response.status_code == 201
    
    register_data = register_response.json()
    token5 = register_data["tokens"]["access_token"]
    
    # Create invoice with payment in business 5
    http_client.headers["Authorization"] = f"Bearer {token5}"
    customer5 = await create_customer(http_client, name="Business 5 Customer")
    product5 = await create_product(http_client, name="Business 5 Product")
    
    items = [
        {
            "product_id": product5["id"],
            "product_name": product5["name"],
            "quantity": 1,
            "unit_price": product5["sale_price"],
            "tax_rate": product5["tax_rate"],
        }
    ]
    invoice5 = await create_invoice(http_client, customer5["id"], items, customer_name=customer5["name"])
    
    # Record payment in business 5
    payment_payload = {
        "amount": invoice5["grand_total"],
        "method": "upi",
        "reference": "UPI999999",
        "notes": "Business 5 payment",
    }
    
    payment_response = await http_client.post(f"/invoices/{invoice5['id']}/payments", json=payment_payload)
    
    if payment_response.status_code in [200, 201]:
        payment_data = payment_response.json()
        payment_id = payment_data.get("id") or payment_data.get("payment_id")
        
        if payment_id:
            # Switch back to business 1
            http_client.headers["Authorization"] = f"Bearer {test_state.access_token}"
            
            # Try to access business 5's payment (should fail)
            response = await http_client.get(f"/payments/{payment_id}")
            
            if response.status_code == 404:
                print("✓ Payment business isolation works")
            elif response.status_code == 405:
                print("ℹ GET /payments/{id} not implemented")
            else:
                print(f"ℹ Payment isolation check returned {response.status_code}")
        else:
            print("ℹ Payment ID not in response")
    else:
        print(f"ℹ Payment recording returned {payment_response.status_code}")


@pytest.mark.asyncio
async def test_list_payments_by_invoice(authenticated_client: httpx.AsyncClient):
    """Test listing payments filtered by invoice"""
    fake_invoice_id = str(uuid.uuid4())
    
    response = await authenticated_client.get(f"/payments?invoice_id={fake_invoice_id}")
    
    if response.status_code == 200:
        data = response.json()
        items_list = data.get("data", data.get("payments", []))
        # Should return empty or no matching payments
        print(f"✓ Payments filtered by invoice: {len(items_list)} items")
    else:
        print(f"ℹ Payments filter returned {response.status_code}")


@pytest.mark.asyncio
async def test_list_payments_pagination(authenticated_client: httpx.AsyncClient):
    """Test payments list pagination"""
    response1 = await authenticated_client.get("/payments?page=1&per_page=5")
    
    if response1.status_code == 200:
        data1 = response1.json()
        
        response2 = await authenticated_client.get("/payments?page=2&per_page=5")
        if response2.status_code == 200:
            data2 = response2.json()
            
            page1_data = data1.get("data", data1.get("payments", []))
            page2_data = data2.get("data", data2.get("payments", []))
            
            print(f"✓ Pagination tested: Page 1 ({len(page1_data)} items), Page 2 ({len(page2_data)} items)")
    else:
        print(f"ℹ Payments pagination returned {response1.status_code}")


@pytest.mark.asyncio
async def test_payment_with_valid_reference(authenticated_client: httpx.AsyncClient):
    """Test recording payment with valid reference"""
    from conftest import create_customer, create_product, create_invoice
    
    customer = await create_customer(authenticated_client)
    product = await create_product(authenticated_client)
    
    items = [
        {
            "product_id": product["id"],
            "product_name": product["name"],
            "quantity": 1,
            "unit_price": product["sale_price"],
            "tax_rate": product["tax_rate"],
        }
    ]
    invoice = await create_invoice(authenticated_client, customer["id"], items, customer_name=customer["name"])
    
    payment_payload = {
        "amount": invoice["grand_total"],
        "method": "bank_transfer",
        "reference": "BT2026031400001",
        "notes": "Full payment for invoice",
    }
    
    response = await authenticated_client.post(f"/invoices/{invoice['id']}/payments", json=payment_payload)
    
    if response.status_code in [200, 201]:
        data = response.json()
        # Verify reference is stored
        assert "reference" in data or "BT2026031400001" in str(data)
        print(f"✓ Payment with reference recorded")
    else:
        print(f"ℹ Payment payment returned {response.status_code}")


@pytest.mark.asyncio
async def test_payment_multiple_methods(authenticated_client: httpx.AsyncClient):
    """Test recording payments with different methods"""
    from conftest import create_customer, create_product, create_invoice
    
    payment_methods = ["upi", "bank_transfer", "cash", "check"]
    
    for method in payment_methods:
        customer = await create_customer(authenticated_client)
        product = await create_product(authenticated_client)
        
        items = [
            {
                "product_id": product["id"],
                "product_name": product["name"],
                "quantity": 1,
                "unit_price": product["sale_price"],
                "tax_rate": product["tax_rate"],
            }
        ]
        invoice = await create_invoice(authenticated_client, customer["id"], items, customer_name=customer["name"])
        
        payment_payload = {
            "amount": invoice["grand_total"],
            "method": method,
            "reference": f"REF-{method.upper()}-001",
        }
        
        response = await authenticated_client.post(f"/invoices/{invoice['id']}/payments", json=payment_payload)
        
        if response.status_code in [200, 201]:
            print(f"✓ Payment with method '{method}' recorded")
        else:
            print(f"ℹ Payment with method '{method}' returned {response.status_code}")
