"""Offline-First Blind E2EE Data Sync Endpoints."""

from datetime import datetime, timezone
from typing import Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy import select
from sqlalchemy.dialects.sqlite import insert as sqlite_insert
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.sync_blob import EncryptedSyncRecord
from app.models.user import User
from app.schemas.sync import (
    AppIdLiteral,
    EncryptedRecordPayload,
    SyncPullResponse,
    SyncPushRequest,
)

router = APIRouter()


@router.post(
    "/push",
    status_code=status.HTTP_200_OK,
    summary="Push Blind Ciphertext Blobs",
    description="Blindly store encrypted record payloads without server-side decryption capability.",
)
async def push_sync_records(
    payload: SyncPushRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Upsert blind encrypted records into user storage vault."""
    for record in payload.records:
        stmt = select(EncryptedSyncRecord).where(
            EncryptedSyncRecord.user_id == current_user.id,
            EncryptedSyncRecord.app_id == record.app_id,
            EncryptedSyncRecord.collection_id == record.collection_id,
            EncryptedSyncRecord.record_id == record.record_id,
        )
        result = await db.execute(stmt)
        existing = result.scalar_one_or_none()

        if existing:
            # Last-write-wins or monotonic version check
            if record.version >= existing.version:
                existing.ciphertext = record.ciphertext
                existing.iv = record.iv
                existing.auth_tag = record.auth_tag
                existing.version = record.version
                existing.device_id = record.device_id
                existing.is_deleted = record.is_deleted
                existing.updated_at = datetime.now(timezone.utc)
        else:
            new_record = EncryptedSyncRecord(
                user_id=current_user.id,
                app_id=record.app_id,
                collection_id=record.collection_id,
                record_id=record.record_id,
                ciphertext=record.ciphertext,
                iv=record.iv,
                auth_tag=record.auth_tag,
                version=record.version,
                device_id=record.device_id,
                is_deleted=record.is_deleted,
            )
            db.add(new_record)

    await db.commit()
    return {"status": "success", "processed_records": len(payload.records)}


@router.get(
    "/pull",
    response_model=SyncPullResponse,
    status_code=status.HTTP_200_OK,
    summary="Pull Blind Ciphertext Blobs",
    description="Retrieve updated encrypted record payloads since a given timestamp or cursor.",
)
async def pull_sync_records(
    app_id: AppIdLiteral = Query(..., description="Application identifier"),
    since: Optional[datetime] = Query(
        default=None, description="Fetch records updated strictly after this timestamp"
    ),
    limit: int = Query(default=100, ge=1, le=500, description="Page limit"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Retrieve blind encrypted records updated after cursor."""
    query = (
        select(EncryptedSyncRecord)
        .where(
            EncryptedSyncRecord.user_id == current_user.id,
            EncryptedSyncRecord.app_id == app_id,
        )
        .order_by(EncryptedSyncRecord.updated_at.asc())
        .limit(limit)
    )

    if since:
        query = query.where(EncryptedSyncRecord.updated_at > since)

    result = await db.execute(query)
    records = result.scalars().all()

    record_payloads = [
        EncryptedRecordPayload(
            app_id=r.app_id,  # type: ignore
            collection_id=r.collection_id,
            record_id=r.record_id,
            ciphertext=r.ciphertext,
            iv=r.iv,
            auth_tag=r.auth_tag,
            version=r.version,
            device_id=r.device_id,
            is_deleted=r.is_deleted,
        )
        for r in records
    ]

    cursor = records[-1].updated_at if records else since
    has_more = len(records) == limit

    return SyncPullResponse(
        records=record_payloads,
        cursor=cursor,
        has_more=has_more,
    )
