"""Public Federated Record Endpoints (Zone 2)."""

import json
from datetime import datetime, timezone
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.core.security import canonicalize_json, verify_ed25519_signature
from app.db.session import get_db
from app.models.public_record import PublicRecord
from app.models.user import User
from app.schemas.records import (
    PublicRecordCreateRequest,
    PublicRecordListResponse,
    PublicRecordResponse,
)

router = APIRouter()


@router.post(
    "",
    response_model=PublicRecordResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Publish Public Record",
    description="Publish signed verifiable public record with Ed25519 cryptographic signature check.",
)
async def create_public_record(
    payload: PublicRecordCreateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Verify cryptographic signature and persist public record."""
    if not current_user.signing_key_ed25519:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User must register an Ed25519 signing key before publishing public records.",
        )

    # Compute deterministic canonical bytes of content JSON
    canonical_bytes = canonicalize_json(payload.content)

    # Verify Ed25519 signature
    is_valid_sig = verify_ed25519_signature(
        public_key_b64=current_user.signing_key_ed25519,
        data=canonical_bytes,
        signature_b64=payload.signature,
    )
    if not is_valid_sig:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Signature verification failed: invalid Ed25519 signature over canonical content.",
        )

    # Check for existing record to upsert
    stmt = select(PublicRecord).where(
        PublicRecord.did == current_user.did,
        PublicRecord.collection == payload.collection,
        PublicRecord.record_id == payload.record_id,
    )
    result = await db.execute(stmt)
    existing_record = result.scalar_one_or_none()

    canonical_str = canonical_bytes.decode("utf-8")

    if existing_record:
        existing_record.content_json = canonical_str
        existing_record.signature = payload.signature
        existing_record.updated_at = datetime.now(timezone.utc)
        record = existing_record
    else:
        record = PublicRecord(
            did=current_user.did,
            collection=payload.collection,
            record_id=payload.record_id,
            content_json=canonical_str,
            signature=payload.signature,
        )
        db.add(record)

    await db.commit()
    await db.refresh(record)

    return PublicRecordResponse(
        id=record.id,
        did=record.did,
        collection=record.collection,
        record_id=record.record_id,
        content=json.loads(record.content_json),
        signature=record.signature,
        created_at=record.created_at,
        updated_at=record.updated_at,
    )


@router.get(
    "/{did}/{collection}",
    response_model=PublicRecordListResponse,
    status_code=status.HTTP_200_OK,
    summary="List Public Records",
    description="Retrieve public verifiable records by author DID and collection name.",
)
async def list_public_records(
    did: str,
    collection: str,
    limit: int = Query(default=50, ge=1, le=200, description="Page limit"),
    offset: int = Query(default=0, ge=0, description="Page offset"),
    db: AsyncSession = Depends(get_db),
):
    """Return paginated list of signed public records."""
    stmt = (
        select(PublicRecord)
        .where(PublicRecord.did == did, PublicRecord.collection == collection)
        .order_by(PublicRecord.created_at.desc())
        .offset(offset)
        .limit(limit)
    )
    result = await db.execute(stmt)
    records = result.scalars().all()

    record_responses = [
        PublicRecordResponse(
            id=r.id,
            did=r.did,
            collection=r.collection,
            record_id=r.record_id,
            content=json.loads(r.content_json),
            signature=r.signature,
            created_at=r.created_at,
            updated_at=r.updated_at,
        )
        for r in records
    ]

    return PublicRecordListResponse(records=record_responses, total=len(record_responses))


@router.get(
    "/{did}/{collection}/{record_id}",
    response_model=PublicRecordResponse,
    status_code=status.HTTP_200_OK,
    summary="Get Public Record",
    description="Retrieve a single verifiable public record by author DID, collection, and record ID.",
)
async def get_public_record(
    did: str,
    collection: str,
    record_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Retrieve single record."""
    stmt = select(PublicRecord).where(
        PublicRecord.did == did,
        PublicRecord.collection == collection,
        PublicRecord.record_id == record_id,
    )
    result = await db.execute(stmt)
    record = result.scalar_one_or_none()

    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Record '{record_id}' not found in collection '{collection}' for DID '{did}'.",
        )

    return PublicRecordResponse(
        id=record.id,
        did=record.did,
        collection=record.collection,
        record_id=record.record_id,
        content=json.loads(record.content_json),
        signature=record.signature,
        created_at=record.created_at,
        updated_at=record.updated_at,
    )
