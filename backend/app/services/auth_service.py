from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi import HTTPException, status
from jose import JWTError

from app.models.user import User, UserRole
from app.models.business import Business
from app.core.security import hash_password, verify_password, create_access_token, create_refresh_token, decode_token
from app.schemas.auth import RegisterRequest, LoginRequest, AuthResponse, UserResponse, BusinessResponse, TokenResponse

# ─────────────────────────────────────────
# Auth Service – Business Logic
# ─────────────────────────────────────────

class AuthService:

    @staticmethod
    async def register(payload: RegisterRequest, db: AsyncSession) -> AuthResponse:
        # Check if email already exists
        existing = await db.execute(select(User).where(User.email == payload.email))
        if existing.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Email already registered"
            )

        # Create business (tenant)
        business = Business(name=payload.business_name, email=payload.email)
        db.add(business)
        await db.flush()  # Get business.id before committing

        # Create user (owner)
        user = User(
            email=payload.email,
            name=payload.name,
            phone=payload.phone,
            password_hash=hash_password(payload.password),
            role=UserRole.OWNER,
            business_id=business.id,
        )
        db.add(user)
        await db.commit()
        await db.refresh(user)
        await db.refresh(business)

        # Generate tokens
        token_data = {"sub": str(user.id), "tenant_id": str(business.id), "role": user.role.value}
        tokens = TokenResponse(
            access_token=create_access_token(token_data),
            refresh_token=create_refresh_token(token_data),
        )

        return AuthResponse(
            user=UserResponse(
                id=str(user.id), email=user.email, name=user.name,
                phone=user.phone, role=user.role.value, business_id=str(user.business_id),
            ),
            business=BusinessResponse(
                id=str(business.id), name=business.name, phone=business.phone,
                email=business.email, gstin=business.gstin,
                address=business.address, city=business.city, state=business.state,
                pincode=business.pincode, pan=business.pan, logo_url=business.logo_url,
                description=business.description, country=business.country,
            ),
            tokens=tokens,
        )

    @staticmethod
    async def login(payload: LoginRequest, db: AsyncSession) -> AuthResponse:
        # Find user
        result = await db.execute(select(User).where(User.email == payload.email))
        user = result.scalar_one_or_none()

        if not user or not verify_password(payload.password, user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )

        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Account is deactivated"
            )

        # Load business
        result = await db.execute(select(Business).where(Business.id == user.business_id))
        business = result.scalar_one()

        # Generate tokens
        token_data = {"sub": str(user.id), "tenant_id": str(business.id), "role": user.role.value}
        tokens = TokenResponse(
            access_token=create_access_token(token_data),
            refresh_token=create_refresh_token(token_data),
        )

        return AuthResponse(
            user=UserResponse(
                id=str(user.id), email=user.email, name=user.name,
                phone=user.phone, role=user.role.value, business_id=str(user.business_id),
            ),
            business=BusinessResponse(
                id=str(business.id), name=business.name, phone=business.phone,
                email=business.email, gstin=business.gstin,
                address=business.address, city=business.city, state=business.state,
                pincode=business.pincode, pan=business.pan, logo_url=business.logo_url,
                description=business.description, country=business.country,
            ),
            tokens=tokens,
        )

    @staticmethod
    async def refresh_token(refresh_token: str, db: AsyncSession) -> TokenResponse:
        try:
            payload = decode_token(refresh_token)
            if payload.get("type") != "refresh":
                raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token type")

            user_id = payload.get("sub")
            tenant_id = payload.get("tenant_id")

            # Verify user still exists and is active
            result = await db.execute(select(User).where(User.id == user_id))
            user = result.scalar_one_or_none()
            if not user or not user.is_active:
                raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")

            token_data = {"sub": str(user.id), "tenant_id": tenant_id, "role": user.role.value}
            return TokenResponse(
                access_token=create_access_token(token_data),
                refresh_token=create_refresh_token(token_data),
            )
        except JWTError:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")

    @staticmethod
    async def get_current_user(user_id: str, db: AsyncSession) -> UserResponse:
        result = await db.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

        return UserResponse(
            id=str(user.id), email=user.email, name=user.name,
            phone=user.phone, role=user.role.value, business_id=str(user.business_id),
        )
