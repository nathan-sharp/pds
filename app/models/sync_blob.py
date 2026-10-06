"""Opaque End-to-End Encrypted (E2EE) Sync Blob Model."""

import uuid
from datetime import datetime, timezone
from sqlalchemy import BigInteger, Boolean, DateTime, ForeignKey, Index, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class EncryptedSyncRecord(Base):
    """Blind encrypted data record for offline-first sync across ARC clients."""

    __tablename__ = "encrypted_sync_records"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    user_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("users.id"), index=True, nullable=False
    )
    
    # Target client application: chirp, burrow, scratch, scout, echo, flock
    app_id: Mapped[str] = mapped_column(String(64), index=True, nullable=False)

    # Logical collection within client (e.g., messages, notes, file_chunks)
    collection_id: Mapped[str] = mapped_column(String(64), index=True, nullable=False)

    # Client-generated record ID (e.g., note UUID, message UUID)
    record_id: Mapped[str] = mapped_column(String(128), index=True, nullable=False)

    # Opaque ciphertext payload (server cannot decrypt)
    ciphertext: Mapped[str] = mapped_column(Text, nullable=False)

    # Cryptographic Initialization Vector (IV) / Nonce
    iv: Mapped[str] = mapped_column(String(64), nullable=False)

    # Authentication Tag for Authenticated Encryption (AEAD)
    auth_tag: Mapped[str] = mapped_column(String(64), nullable=False)

    # Lamport timestamp or monotonic sequence number for conflict resolution
    version: Mapped[int] = mapped_column(BigInteger, default=1, nullable=False)

    # Device ID that authored the record update
    device_id: Mapped[str] = mapped_column(String(64), nullable=False)

    # Tombstone flag for distributed deletion syncing
    is_deleted: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    __table_args__ = (
        Index(
            "idx_user_app_collection_record",
            "user_id",
            "app_id",
            "collection_id",
            "record_id",
            unique=True,
        ),
        Index("idx_sync_sync_cursor", "user_id", "app_id", "updated_at"),
    )
