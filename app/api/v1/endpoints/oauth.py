"""OAuth 2.0 PKCE Endpoints for 'Log in with your PDS' Single Sign-On."""

from datetime import datetime, timedelta, timezone
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.security import (
    create_access_token,
    generate_secure_token,
    verify_password,
    verify_pkce,
)
from app.db.session import get_db
from app.models.oauth import OAuthAuthorizationCode, OAuthClient, OAuthRefreshToken
from app.models.user import User
from app.schemas.auth import TokenResponse
from app.schemas.oauth import (
    OAuthAuthorizeRequest,
    OAuthAuthorizeResponse,
    OAuthTokenExchangeRequest,
)

router = APIRouter()


@router.post(
    "/authorize",
    response_model=OAuthAuthorizeResponse,
    status_code=status.HTTP_200_OK,
    summary="Authorize Client App (PDS SSO)",
    description="Authenticate PDS user and issue authorization code for client applications (RFC 7636).",
)
async def authorize_client(
    payload: OAuthAuthorizeRequest,
    db: AsyncSession = Depends(get_db),
):
    """Validate client application and issue PKCE authorization code."""
    # Validate client identifier against approved ARC suite list
    if payload.client_id not in settings.ALLOWED_CLIENT_IDS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unauthorized client_id '{payload.client_id}'.",
        )

    # Authenticate user credentials
    stmt = select(User).where(User.pds_id == payload.pds_id)
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()

    if not user or not verify_password(payload.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid PDS credentials",
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is deactivated",
        )

    # Ensure client record exists in database
    client_stmt = select(OAuthClient).where(OAuthClient.client_id == payload.client_id)
    client_res = await db.execute(client_stmt)
    client = client_res.scalar_one_or_none()
    if not client:
        client = OAuthClient(
            client_id=payload.client_id,
            client_name=payload.client_id.capitalize(),
            redirect_uris=payload.redirect_uri,
            is_active=True,
        )
        db.add(client)
        await db.flush()

    # Generate cryptographically secure authorization code (256 bits entropy)
    auth_code_str = generate_secure_token(32)
    code_record = OAuthAuthorizationCode(
        code=auth_code_str,
        client_id=payload.client_id,
        user_id=user.id,
        redirect_uri=payload.redirect_uri,
        code_challenge=payload.code_challenge,
        code_challenge_method=payload.code_challenge_method,
        scope=payload.scope,
        expires_at=datetime.now(timezone.utc) + timedelta(minutes=5),
        is_used=False,
    )
    db.add(code_record)
    await db.commit()

    return OAuthAuthorizeResponse(
        code=auth_code_str,
        state=payload.state,
        redirect_uri=payload.redirect_uri,
    )


@router.post(
    "/token",
    response_model=TokenResponse,
    status_code=status.HTTP_200_OK,
    summary="Exchange Authorization Code for Token",
    description="Exchange PKCE authorization code for scoped JWT access token and refresh token.",
)
async def exchange_token(
    payload: OAuthTokenExchangeRequest,
    db: AsyncSession = Depends(get_db),
):
    """Verify PKCE challenge and issue access/refresh tokens."""
    if payload.grant_type == "authorization_code":
        if not payload.code or not payload.code_verifier:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Parameters 'code' and 'code_verifier' are required for authorization_code grant.",
            )

        # Retrieve authorization code record
        stmt = select(OAuthAuthorizationCode).where(
            OAuthAuthorizationCode.code == payload.code,
            OAuthAuthorizationCode.client_id == payload.client_id,
        )
        result = await db.execute(stmt)
        auth_code = result.scalar_one_or_none()

        if not auth_code:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid authorization code",
            )

        # Verify code usage and expiration
        now = datetime.now(timezone.utc)
        if auth_code.is_used:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Authorization code has already been consumed",
            )
        if auth_code.expires_at < now:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Authorization code has expired",
            )

        # Verify PKCE challenge
        pkce_valid = verify_pkce(
            code_verifier=payload.code_verifier,
            code_challenge=auth_code.code_challenge,
            method=auth_code.code_challenge_method,
        )
        if not pkce_valid:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="PKCE verification failed: invalid code_verifier",
            )

        # Invalidate authorization code
        auth_code.is_used = True

        # Generate tokens
        access_token = create_access_token(
            subject=auth_code.user_id,
            client_id=auth_code.client_id,
            expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
        )

        refresh_token_value = generate_secure_token(32)
        refresh_token = OAuthRefreshToken(
            token=refresh_token_value,
            client_id=auth_code.client_id,
            user_id=auth_code.user_id,
            expires_at=now + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS),
            is_revoked=False,
        )
        db.add(refresh_token)
        await db.commit()

        return TokenResponse(
            access_token=access_token,
            token_type="Bearer",
            expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            refresh_token=refresh_token_value,
            scope=auth_code.scope,
        )

    elif payload.grant_type == "refresh_token":
        if not payload.refresh_token:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Parameter 'refresh_token' is required for refresh_token grant.",
            )

        stmt = select(OAuthRefreshToken).where(
            OAuthRefreshToken.token == payload.refresh_token,
            OAuthRefreshToken.client_id == payload.client_id,
            OAuthRefreshToken.is_revoked.is_(False),
        )
        result = await db.execute(stmt)
        token_rec = result.scalar_one_or_none()

        now = datetime.now(timezone.utc)
        if not token_rec or token_rec.expires_at < now:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired refresh token",
            )

        # Rotate refresh token
        token_rec.is_revoked = True
        new_refresh_token_value = generate_secure_token(32)
        new_refresh_token = OAuthRefreshToken(
            token=new_refresh_token_value,
            client_id=token_rec.client_id,
            user_id=token_rec.user_id,
            expires_at=now + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS),
            is_revoked=False,
        )
        db.add(new_refresh_token)

        access_token = create_access_token(
            subject=token_rec.user_id,
            client_id=token_rec.client_id,
            expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
        )
        await db.commit()

        return TokenResponse(
            access_token=access_token,
            token_type="Bearer",
            expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            refresh_token=new_refresh_token_value,
            scope="openid sync",
        )

    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail=f"Unsupported grant_type '{payload.grant_type}'.",
    )
