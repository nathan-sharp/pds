"""Webhook Subscription Model."""

import uuid
from datetime import datetime, timezone
from sqlalchemy import Boolean, DateTime, ForeignKey, String, JSON
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class WebhookSubscription(Base):
    """Webhook subscription for real-time event delivery."""

    __tablename__ = "webhook_subscriptions"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    user_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("users.id"), index=True, nullable=False
    )
    target_url: Mapped[str] = mapped_column(String(2048), nullable=False)

    # List of events the webhook subscribes to (e.g., ["record.created", "record.updated"])
    events: Mapped[list[str]] = mapped_column(JSON, nullable=False)

    # Secret used to sign webhook payloads (HMAC-SHA256)
    secret: Mapped[str] = mapped_column(String(64), nullable=False)

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
