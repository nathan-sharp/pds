"""Blind E2EE Data Sync Schemas for ARC Clients."""

from datetime import datetime
from typing import List, Literal, Optional
from pydantic import BaseModel, ConfigDict, Field

AppIdLiteral = Literal["chirp", "burrow", "scratch", "scout", "echo", "flock"]


class EncryptedRecordPayload(BaseModel):
    """Opaque encrypted data unit."""

    model_config = ConfigDict(extra="forbid")

    app_id: AppIdLiteral = Field(
        ..., description="Client application identifier"
    )
    collection_id: str = Field(
        ...,
        min_length=1,
        max_length=64,
        pattern=r"^[a-zA-Z0-9_\-]+$",
        description="Logical collection name (e.g. notes, messages)",
    )
    record_id: str = Field(
        ...,
        min_length=1,
        max_length=128,
        description="Client-side UUID or identifier for the record",
    )
    ciphertext: str = Field(..., description="Encrypted payload in Base64 encoding")
    iv: str = Field(
        ..., min_length=12, max_length=64, description="Cryptographic nonce / IV"
    )
    auth_tag: str = Field(
        ..., min_length=16, max_length=64, description="AEAD authentication tag"
    )
    version: int = Field(
        default=1, ge=1, description="Monotonic version or Lamport timestamp"
    )
    device_id: str = Field(
        ..., min_length=1, max_length=64, description="Originating client device identifier"
    )
    is_deleted: bool = Field(
        default=False, description="Tombstone flag for distributed deletion"
    )


class SyncPushRequest(BaseModel):
    """Batch upload of opaque encrypted records."""

    model_config = ConfigDict(extra="forbid")

    records: List[EncryptedRecordPayload] = Field(
        ..., max_length=100, description="List of encrypted records to persist"
    )


class SyncPullResponse(BaseModel):
    """Batch download of updated encrypted records."""

    model_config = ConfigDict(extra="forbid")

    records: List[EncryptedRecordPayload]
    cursor: Optional[datetime]
    has_more: bool
