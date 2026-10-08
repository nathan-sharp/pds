"""Public Federated Record Model (Zone 2)."""

import uuid
from datetime import datetime, timezone
from sqlalchemy import DateTime, Index, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class PublicRecord(Base):
    """Signed public federated record published under a W3C Decentralized Identifier (DID)."""

    __tablename__ = "public_records"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    did: Mapped[str] = mapped_column(String(256), index=True, nullable=False)
    collection: Mapped[str] = mapped_column(String(128), index=True, nullable=False)
    record_id: Mapped[str] = mapped_column(String(128), index=True, nullable=False)

    # Canonical JSON string of the record payload
    content_json: Mapped[str] = mapped_column(Text, nullable=False)

    # Base64-encoded Ed25519 signature over canonical content_json
    signature: Mapped[str] = mapped_column(String(256), nullable=False)

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
            "idx_public_record_did_collection_record",
            "did",
            "collection",
            "record_id",
            unique=True,
        ),
        Index("idx_public_record_feed", "collection", "created_at"),
    )
