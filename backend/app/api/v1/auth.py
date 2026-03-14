from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.middleware.auth import get_current_user_context, TokenData
from app.schemas.auth import (
    RegisterRequest, LoginRequest, RefreshTokenRequest,
    AuthResponse, TokenResponse, UserResponse,
)
from app.services.auth_service import AuthService

# ─────────────────────────────────────────
# Auth Router
# ─────────────────────────────────────────

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/register", response_model=AuthResponse, status_code=201)
async def register(payload: RegisterRequest, db: AsyncSession = Depends(get_db)):
    """Register a new user and create their business (tenant)."""
    return await AuthService.register(payload, db)

@router.post("/login", response_model=AuthResponse)
async def login(payload: LoginRequest, db: AsyncSession = Depends(get_db)):
    """Authenticate user and return JWT tokens."""
    return await AuthService.login(payload, db)

@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(payload: RefreshTokenRequest, db: AsyncSession = Depends(get_db)):
    """Exchange a refresh token for a new access + refresh token pair."""
    return await AuthService.refresh_token(payload.refresh_token, db)

@router.get("/me", response_model=UserResponse)
async def get_me(
    current_user: TokenData = Depends(get_current_user_context),
    db: AsyncSession = Depends(get_db),
):
    """Get the currently authenticated user's profile."""
    return await AuthService.get_current_user(current_user.user_id, db)
