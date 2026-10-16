"""Webhook Schemas."""

from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, HttpUrl, Field


class WebhookCreate(BaseModel):
    """Schema for creating a new webhook subscription."""

    target_url: HttpUrl = Field(
        ...,
        description="The destination URL where webhook payloads will be sent."
    )
    events: List[str] = Field(
        ...,
        min_length=1,
        description="List of event topics to subscribe to (e.g., ['record.created'])."
    )
    secret: Optional[str] = Field(
        None,
        description="Optional pre-shared secret. If not provided, the server will generate one.",
        max_length=64,
    )


class WebhookResponse(BaseModel):
    """Schema for returning a webhook subscription."""

    id: str
    target_url: HttpUrl
    events: List[str]
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class WebhookResponseWithSecret(WebhookResponse):
    """Schema for returning a newly created webhook subscription, including the secret."""

    secret: str
