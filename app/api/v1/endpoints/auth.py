"""PDS ID Direct Authentication Endpoints."""

from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.core.config import settings
from app.core.security import (
    create_access_token,
    generate_secure_token,
    hash_password,
    verify_password,
)
from app.db.session import get_db
from app.models.oauth import OAuthRefreshToken
from app.models.user import User
from app.schemas.auth import (
    TokenResponse,
    UserLoginRequest,
    UserRegisterRequest,
    UserResponse,
)

router = APIRouter()


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register PDS ID",
    description="Provision a new self-hosted PDS ID identity with Argon2id credential hashing.",
)
async def register_user(
    payload: UserRegisterRequest,
    db: AsyncSession = Depends(get_db),
):
    """Register unique PDS ID."""
    stmt = select(User).where(User.pds_id == payload.pds_id)
    result = await db.execute(stmt)
    existing_user = result.scalar_one_or_none()

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="PDS ID is already registered on this node",
        )

    # Argon2id password hashing
    password_digest = hash_password(payload.password)

    user = User(
        pds_id=payload.pds_id,
        hashed_password=password_digest,
        public_identity_key=payload.public_identity_key,
        encrypted_key_envelope=payload.encrypted_key_envelope,
        is_active=True,
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)

    return user


@router.post(
    "/login",
    response_model=TokenResponse,
    status_code=status.HTTP_200_OK,
    summary="Direct PDS ID Login",
    description="Authenticate master credentials and issue signed JWT access token.",
)
async def login_user(
    payload: UserLoginRequest,
    db: AsyncSession = Depends(get_db),
):
    """Authenticate PDS user and issue Bearer token."""
    stmt = select(User).where(User.pds_id == payload.pds_id)
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()

    if not user or not verify_password(payload.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid PDS ID or passphrase",
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is disabled",
        )

    access_token = create_access_token(subject=user.id)
    refresh_token_value = generate_secure_token(32)

    return TokenResponse(
        access_token=access_token,
        token_type="Bearer",
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        refresh_token=refresh_token_value,
        scope="pds:full",
    )


@router.get(
    "/me",
    response_model=UserResponse,
    status_code=status.HTTP_200_OK,
    summary="Get Active PDS Profile",
    description="Retrieve public profile and encrypted key envelopes for authenticated user.",
)
async def get_me(current_user: User = Depends(get_current_user)):
    """Return active user profile."""
    return current_user
