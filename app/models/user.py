"""User ORM Model."""

import uuid
from datetime import datetime, timezone
from sqlalchemy import Boolean, DateTime, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class User(Base):
    """User account entity representing a PDS identity."""

    __tablename__ = "users"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    pds_id: Mapped[str] = mapped_column(
        String(128), unique=True, index=True, nullable=False
    )
    did: Mapped[str] = mapped_column(
        String(256), unique=True, index=True, nullable=False
    )
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    
    # Public identity keys for W3C did:web documents
    signing_key_ed25519: Mapped[str] = mapped_column(String(128), nullable=True)
    encryption_key_x25519: Mapped[str] = mapped_column(String(128), nullable=True)

    # Legacy public identity key (retained for backward compatibility)
    public_identity_key: Mapped[str] = mapped_column(Text, nullable=True)

    # Encrypted Master Key (EMK) envelope stored blindly for cross-device key sync
    encrypted_key_envelope: Mapped[str] = mapped_column(Text, nullable=True)

    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
