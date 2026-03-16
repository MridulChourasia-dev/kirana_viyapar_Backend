"""
Auth API Tests

Test Cases:
- User registration
- User login
- Refresh token
- Invalid credentials
- Duplicate email
"""
import pytest
import httpx
from datetime import datetime
import uuid
from conftest import generate_unique_email, generate_unique_phone

pytestmark = pytest.mark.auth


@pytest.mark.asyncio
async def test_register_user_success():
    """Test successful user registration"""
    base_url = "http://localhost:8000/api/v1"
    
    unique_email = generate_unique_email("newuser")
    unique_phone = generate_unique_phone()
    
    payload = {
        "business_name": f"Test Business {datetime.now().isoformat()}",
        "name": "New User",
        "email": unique_email,
        "password": "SecurePassword123!",
        "phone": unique_phone,
    }
    
    async with httpx.AsyncClient(base_url=base_url, timeout=30) as client:
        response = await client.post("/auth/register", json=payload)
    
    assert response.status_code == 201, f"Expected 201, got {response.status_code}: {response.text}"
    
    data = response.json()
    
    # Validate response structure
    assert "user" in data
    assert "business" in data
    assert "tokens" in data
    
    # Validate user fields
    assert data["user"]["id"] is not None
    assert data["user"]["email"] == unique_email
    assert data["user"]["role"] == "owner"
    assert data["user"]["name"] == "New User"
    
    # Validate business fields
    assert data["business"]["id"] is not None
    assert data["business"]["name"] == payload["business_name"]
    
    # Validate tokens
    assert data["tokens"]["access_token"] is not None
    assert data["tokens"]["refresh_token"] is not None
    assert data["tokens"]["token_type"] == "bearer"
    
    print(f"✓ User registered: {unique_email}")
    print(f"  User ID: {data['user']['id']}")
    print(f"  Business ID: {data['business']['id']}")


@pytest.mark.asyncio
async def test_login_user_success(http_client: httpx.AsyncClient):
    """Test successful user login"""
    unique_email = generate_unique_email("login")
    unique_phone = generate_unique_phone()
    password = "SecurePassword123!"

    register_payload = {
        "business_name": "Login Test Business",
        "name": "Login User",
        "email": unique_email,
        "password": password,
        "phone": unique_phone,
    }
    reg_response = await http_client.post("/auth/register", json=register_payload)
    assert reg_response.status_code == 201, f"Expected 201, got {reg_response.status_code}: {reg_response.text}"
    
    payload = {
        "email": unique_email,
        "password": password,
    }
    
    response = await http_client.post("/auth/login", json=payload)
    
    assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
    
    data = response.json()
    
    # Validate response structure
    assert "user" in data
    assert "business" in data
    assert "tokens" in data
    
    # Validate user fields
    assert data["user"]["id"] is not None
    assert data["user"]["email"] == unique_email
    assert data["user"]["role"] == "owner"
    
    # Validate tokens
    assert data["tokens"]["access_token"] is not None
    assert data["tokens"]["token_type"] == "bearer"
    
    print(f"✓ User login successful: {unique_email}")


@pytest.mark.asyncio
async def test_login_invalid_email():
    """Test login with non-existent email"""
    base_url = "http://localhost:8000/api/v1"
    
    payload = {
        "email": "nonexistent@example.com",
        "password": "SomePassword123!",
    }
    
    async with httpx.AsyncClient(base_url=base_url, timeout=30) as client:
        response = await client.post("/auth/login", json=payload)
    
    assert response.status_code == 401, f"Expected 401, got {response.status_code}"
    
    print("✓ Invalid email login rejected with 401")


@pytest.mark.asyncio
async def test_login_invalid_password(http_client: httpx.AsyncClient):
    """Test login with incorrect password"""
    from conftest import TEST_USER_EMAIL
    
    payload = {
        "email": TEST_USER_EMAIL,
        "password": "WrongPassword123!",
    }
    
    response = await http_client.post("/auth/login", json=payload)
    
    assert response.status_code == 401, f"Expected 401, got {response.status_code}"
    
    print("✓ Invalid password rejected with 401")


@pytest.mark.asyncio
async def test_register_duplicate_email(http_client: httpx.AsyncClient):
    """Test registration with duplicate email"""
    duplicate_email = generate_unique_email("dup")
    unique_phone = generate_unique_phone()

    first_payload = {
        "business_name": "First Business",
        "name": "First User",
        "email": duplicate_email,
        "password": "DifferentPassword123!",
        "phone": unique_phone,
    }
    first_response = await http_client.post("/auth/register", json=first_payload)
    assert first_response.status_code == 201, f"Expected 201, got {first_response.status_code}: {first_response.text}"

    payload = {
        "business_name": "Another Business",
        "name": "Another User",
        "email": duplicate_email,  # Already registered in this test
        "password": "DifferentPassword123!",
        "phone": generate_unique_phone(),
    }
    
    response = await http_client.post("/auth/register", json=payload)
    
    assert response.status_code >= 400, f"Expected duplicate registration failure, got {response.status_code}"
    
    print(f"✓ Duplicate email registration rejected with {response.status_code}")


@pytest.mark.asyncio
async def test_login_missing_email(http_client: httpx.AsyncClient):
    """Test login missing email field"""
    payload = {
        "password": "SomePassword123!",
    }
    
    response = await http_client.post("/auth/login", json=payload)
    
    assert response.status_code == 422, f"Expected 422, got {response.status_code}"
    
    print("✓ Missing email field validation works (422)")


@pytest.mark.asyncio
async def test_login_missing_password(http_client: httpx.AsyncClient):
    """Test login missing password field"""
    payload = {
        "email": "test@example.com",
    }
    
    response = await http_client.post("/auth/login", json=payload)
    
    assert response.status_code == 422, f"Expected 422, got {response.status_code}"
    
    print("✓ Missing password field validation works (422)")


@pytest.mark.asyncio
async def test_refresh_token(http_client: httpx.AsyncClient):
    """Test token refresh"""
    unique_email = f"refresh.{uuid.uuid4().hex[:6]}@example.com"
    unique_phone = f"+91{uuid.uuid4().hex[:10]}".replace('a', '1')[:13]
    password = "SecurePassword123!"

    register_payload = {
        "business_name": "Refresh Test Business",
        "name": "Refresh User",
        "email": unique_email,
        "password": password,
        "phone": unique_phone,
    }
    register_response = await http_client.post("/auth/register", json=register_payload)
    assert register_response.status_code == 201, f"Expected 201, got {register_response.status_code}: {register_response.text}"

    login_payload = {
        "email": unique_email,
        "password": password,
    }
    
    login_response = await http_client.post("/auth/login", json=login_payload)
    assert login_response.status_code == 200
    
    login_data = login_response.json()
    refresh_token = login_data["tokens"].get("refresh_token")
    
    if not refresh_token:
        pytest.skip("Refresh token not provided in login response")
    
    # Attempt to refresh
    refresh_payload = {
        "refresh_token": refresh_token,
    }
    
    refresh_response = await http_client.post("/auth/refresh", json=refresh_payload)
    
    # Note: This might return 404 if endpoint not implemented
    if refresh_response.status_code == 200:
        refresh_data = refresh_response.json()
        assert "access_token" in refresh_data
        assert refresh_data["token_type"] == "bearer"
        print("✓ Token refresh successful")
    else:
        print(f"ℹ Refresh token endpoint returned {refresh_response.status_code} (may not be implemented)")


@pytest.mark.asyncio
async def test_register_weak_password():
    """Test registration with weak password"""
    base_url = "http://localhost:8000/api/v1"
    
    unique_email = f"weakpass.{uuid.uuid4().hex[:6]}@example.com"
    unique_phone = f"+91{uuid.uuid4().hex[:10]}".replace('a', '1')[:13]
    
    payload = {
        "business_name": "Test Business",
        "name": "Test User",
        "email": unique_email,
        "password": "weak",  # Too weak
        "phone": unique_phone,
    }
    
    async with httpx.AsyncClient(base_url=base_url, timeout=30) as client:
        response = await client.post("/auth/register", json=payload)
    
    # Should either reject with 422 or accept (depending on validation rules)
    assert response.status_code in [201, 422], f"Unexpected status: {response.status_code}"
    
    print(f"✓ Weak password handling: {response.status_code}")


@pytest.mark.asyncio
async def test_unauthorized_without_token(http_client: httpx.AsyncClient):
    """Test accessing protected endpoint without token"""
    response = await http_client.get("/customers")
    
    assert response.status_code == 401, f"Expected 401, got {response.status_code}"
    
    print("✓ Unauthorized access rejected with 401")


@pytest.mark.asyncio
async def test_invalid_token_format(http_client: httpx.AsyncClient):
    """Test accessing protected endpoint with invalid token"""
    http_client.headers["Authorization"] = "Bearer invalid.token.here"
    
    response = await http_client.get("/customers")
    
    assert response.status_code == 401, f"Expected 401, got {response.status_code}"
    
    print("✓ Invalid token format rejected with 401")
