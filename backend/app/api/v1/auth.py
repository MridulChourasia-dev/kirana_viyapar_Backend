from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.middleware.auth import get_current_user_context, TokenData
from app.schemas.auth import (
    RegisterRequest, LoginRequest, RefreshTokenRequest,
    AuthResponse, TokenResponse, UserResponse,
)
from app.services.auth_service import AuthService
from app.core.openapi_docs import RESPONSES_CREATE, RESPONSES_ACTION

# ─────────────────────────────────────────
# Auth Router
# ─────────────────────────────────────────

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post(
    "/register",
    response_model=AuthResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register New User",
    description="Create a new user account and associated business (tenant)",
    responses=RESPONSES_CREATE,
)
async def register(
    payload: RegisterRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    Register a new user and create their business (tenant).
    
    Returns:
    - **access_token**: JWT access token for authenticated requests
    - **refresh_token**: Token to request new access tokens
    - **token_type**: Always 'bearer'
    - **user**: User profile information with business details
    """
    return await AuthService.register(payload, db)

@router.post(
    "/login",
    response_model=AuthResponse,
    summary="User Login",
    description="Authenticate user with email and password",
    responses=RESPONSES_ACTION,
)
async def login(
    payload: LoginRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    Authenticate user and return JWT tokens.
    
    Args:
    - **email**: User email address
    - **password**: User password
    
    Returns:
    - **access_token**: JWT token for authenticated requests
    - **refresh_token**: Long-lived token to request new access tokens
    - **user**: Authenticated user information
    """
    return await AuthService.login(payload, db)

@router.post(
    "/refresh",
    response_model=TokenResponse,
    summary="Refresh Access Token",
    description="Exchange refresh token for new access and refresh tokens",
    responses=RESPONSES_ACTION,
)
async def refresh_token(
    payload: RefreshTokenRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    Exchange a refresh token for a new access + refresh token pair.
    
    This endpoint allows clients to obtain a new access token without
    requiring the user to log in again.
    
    Args:
    - **refresh_token**: Valid refresh token obtained from login
    
    Returns:
    - **access_token**: New JWT access token
    - **refresh_token**: New refresh token
    - **token_type**: Always 'bearer'
    """
    return await AuthService.refresh_token(payload.refresh_token, db)

@router.get(
    "/me",
    response_model=UserResponse,
    summary="Get Current User Profile",
    description="Retrieve authenticated user's profile and business information",
    responses={
        200: {"description": "User profile retrieved successfully"},
        401: {"description": "Unauthorized - Invalid or missing token"},
        500: {"description": "Internal server error"},
    },
)
async def get_me(
    current_user: TokenData = Depends(get_current_user_context),
    db: AsyncSession = Depends(get_db),
):
    """
    Get the currently authenticated user's profile.
    
    Requires valid authentication token in Authorization header.
    
    Returns:
    - **id**: User ID
    - **email**: User email address
    - **business**: Associated business information including tenant_id
    """
    return await AuthService.get_current_user(current_user.user_id, db)
