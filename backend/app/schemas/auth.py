"""
Authentication schemas
"""
import uuid

from pydantic import BaseModel, ConfigDict, EmailStr, Field


# ─────────────────────────────────────────
# Request Schemas
# ─────────────────────────────────────────


class RegisterRequest(BaseModel):
    """User registration request"""

    name: str = Field(..., min_length=2, max_length=255)
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=128)
    phone: str | None = Field(None, max_length=20)
    business_name: str = Field(..., min_length=2, max_length=255)


class LoginRequest(BaseModel):
    """User login request"""

    email: EmailStr
    password: str = Field(..., min_length=6, max_length=128)


class RefreshTokenRequest(BaseModel):
    """Refresh token request"""

    refresh_token: str


# ─────────────────────────────────────────
# Response Schemas
# ─────────────────────────────────────────


class UserResponse(BaseModel):
    """User response schema"""

    model_config = ConfigDict(from_attributes=True, use_enum_values=True)

    id: uuid.UUID
    email: str
    name: str
    phone: str | None
    role: str
    business_id: uuid.UUID


class BusinessResponse(BaseModel):
    """Business response schema"""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    name: str
    email: str
    phone: str | None
    description: str | None
    address: str | None
    city: str | None
    state: str | None
    pincode: str | None
    gstin: str | None
    pan: str | None


class TokenResponse(BaseModel):
    """JWT token response"""

    access_token: str
    refresh_token: str | None = None
    token_type: str = "bearer"
    expires_in: int


class LoginResponse(BaseModel):
    """Login response with user and tokens"""

    user: UserResponse
    business: BusinessResponse
    tokens: TokenResponse

class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"

class AuthResponse(BaseModel):
    user: UserResponse
    business: BusinessResponse
    tokens: TokenResponse
