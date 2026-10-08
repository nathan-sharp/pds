"""W3C Decentralized Identifier (DID) Resolution and Key Management Endpoints."""

from typing import Any, Dict
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.identity import IdentityResponse, RegisterKeysRequest
from app.services.identity_service import build_server_did_document, build_user_did_document

router = APIRouter()


@router.get(
    "/server",
    response_model=Dict[str, Any],
    status_code=status.HTTP_200_OK,
    summary="Get Server DID Document",
    description="Retrieve W3C did:web document for this ARC PDS root node.",
)
async def get_server_did():
    """Return root server DID document."""
    return build_server_did_document()


@router.get(
    "/resolve/{did:path}",
    response_model=Dict[str, Any],
    status_code=status.HTTP_200_OK,
    summary="Resolve W3C DID Document",
    description="Resolve user did:web identifier and return cryptographic keys and service endpoints.",
)
async def resolve_did(
    did: str,
    db: AsyncSession = Depends(get_db),
):
    """Resolve W3C did:web identifier."""
    stmt = select(User).where(User.did == did, User.is_active.is_(True))
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Decentralized identifier '{did}' not found on this server.",
        )

    return build_user_did_document(user)


@router.get(
    "/by-handle/{pds_id}",
    response_model=Dict[str, Any],
    status_code=status.HTTP_200_OK,
    summary="Resolve Handle to DID Document",
    description="Look up user DID document by PDS handle username.",
)
async def resolve_handle(
    pds_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Resolve user by local handle."""
    stmt = select(User).where(User.pds_id == pds_id, User.is_active.is_(True))
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User handle '{pds_id}' not found on this node.",
        )

    return build_user_did_document(user)


@router.post(
    "/keys",
    response_model=IdentityResponse,
    status_code=status.HTTP_200_OK,
    summary="Register Cryptographic Keys",
    description="Register or rotate Ed25519 signing key and X25519 encryption key for authenticated user.",
)
async def register_keys(
    payload: RegisterKeysRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Update user cryptographic public keys and encrypted key envelope."""
    current_user.signing_key_ed25519 = payload.signing_key_ed25519
    current_user.public_identity_key = payload.signing_key_ed25519
    if payload.encryption_key_x25519:
        current_user.encryption_key_x25519 = payload.encryption_key_x25519
    if payload.encrypted_key_envelope:
        current_user.encrypted_key_envelope = payload.encrypted_key_envelope

    await db.commit()
    await db.refresh(current_user)

    return current_user
